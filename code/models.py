import pydantic

class ChannelLocationCCF(pydantic.BaseModel):
    """Basic channel location data matching original output from IBL alignment capsule."""
    x: float
    y: float
    z: float
    axial: float
    lateral: float
    brain_region_id: int
    brain_region: str
    
# import aind_data_schema_models.brain_atlas
# class ChannelLocationCCFDataSchema(pydantic.BaseModel):
#     """Channel location data from IBL alignment capsule instantiated original output, but converted
#     to ."""
#     brain_structure_model: aind_data_schema_models.brain_atlas.BrainStructureModel | None
#     ccf_ap: float
#     ccf_ml: float
#     ccf_dv: float
#     axial: float
#     lateral: float
#     brain_region_id: int = pydantic.Field(exclude=True)
#     brain_region: str = pydantic.Field(exclude=True)

#     @pydantic.computed_field
#     @property
#     def brain_structure_model(
#         self,
#     ) -> aind_data_schema_models.brain_atlas.BrainStructureModel | None:
#         if self.brain_region.lower() in ("void", "out of brain", "unassigned"):
#             return aind_data_schema_models.brain_atlas.BrainStructureModel(
#                 atlas="CCFv3",
#                 id="0",
#                 name="void",
#                 acronym="void",
#             )
#         return aind_data_schema_models.brain_atlas.CCFv3.from_id(self.brain_region)

