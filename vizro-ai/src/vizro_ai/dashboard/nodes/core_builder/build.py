"""Module that contains the builder functionality."""

import logging

import vizro.models as vm
from vizro_ai.utils.helper import DebugFailure

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PageBuilder:
    """Class to build a page."""

    def __init__(self, model, df_metadata, page_plan):
        """Initialize PageBuilder."""
        self._model = model
        self._df_metadata = df_metadata
        self._page_plan = page_plan
        self._components = None
        self._controls = None
        self._page = None
        self._layout = None

    @property
    def components(self):
        """Property to get components."""
        if self._components is None:
            self._components = self._build_components()
        return self._components

    def _build_components(self):
        components = []
        logger.info(f"Building components of page: {self._page_plan.title}")
        # Could potentially be parallelized or sent as a batch to the API
        for i in range(len(self._page_plan.components)):
            logger.info(f"{self._page_plan.title} -> Building component {self._page_plan.components[i]}")
            try:
                components.append(
                    self._page_plan.components[i].create(df_metadata=self._df_metadata, model=self._model)
                )
            except DebugFailure as e:  # TODO: check - does this ever get raised?
                components.append(
                    vm.Card(
                        id=self._page_plan.components[i].component_id, text=f"Failed to build component: {e}"
                    )
                )
        return components

    @property
    def layout(self):
        """Property to get layout."""
        if self._layout is None:
            self._layout = self._build_layout()
        return self._layout

    def _build_layout(self):
        logger.info(f"{self._page_plan.title} -> Building layout {self._page_plan.layout}")
        return self._page_plan.layout.create(model=self._model, df_metadata=self._df_metadata)

    @property
    def controls(self):
        """Property to get controls."""
        if self._controls is None:
            self._controls = self._build_controls()
        return self._controls

    @property
    def available_components(self):
        """Property to get available components."""
        return [comp.id for comp in self.components if isinstance(comp, (vm.Graph, vm.AgGrid))]

    def _build_controls(self):
        controls = []
        logger.info(f"Building controls of page: {self._page_plan.title}")
        # Could potentially be parallelized or sent as a batch to the API
        for i in range(len(self._page_plan.controls)):
            logger.info(f"{self._page_plan.title} -> Building control {self._page_plan.controls[i]}")
            control = self._page_plan.controls[i].create(
                model=self._model, available_components=self.available_components, df_metadata=self._df_metadata
            )
            if control:
                controls.append(control)

        return controls

    @property
    def page(self):
        """Property to get page."""
        if self._page is None:
            logger.info(f"Building page: {self._page_plan.title}")
            self._page = vm.Page(
                title=self._page_plan.title, components=self.components, controls=self.controls, layout=self.layout
            )
        return self._page
