from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy


class Investigation(models.Model):
    class License(models.TextChoices):
        CC_BY = 'BY', gettext_lazy('CC BY 4.0'),
        CC_BY_SA = 'SA', gettext_lazy('CC BY-SA 4.0')
        CC_BY_ND = 'ND', gettext_lazy('CC BY-ND 4.0')
        CC_BY_NC = 'NC', gettext_lazy('CC BY-NC 4.0')
        CC_BY_NC_SA = 'NS', gettext_lazy('CC BY-NC-SA 4.0')
        CC_BY_NC_ND = 'NN', gettext_lazy('CC BY-NC-ND 4.0')

    owner = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    team = models.ManyToManyField(User, related_name='investigation_team', null=True, blank=True)
    unique_id = models.CharField(max_length=255, unique=True, blank=True)
    title = models.CharField(max_length=255, blank=False)
    description = models.TextField(blank=True)
    submission_date = models.DateField(blank=True, null=True)
    public_release_date = models.DateField(blank=True, null=True)
    license = models.CharField(max_length=2, choices=License.choices, default=License.CC_BY)
    miappe_version = models.CharField(max_length=50, blank=True, default='1.1')
    associated_publication = models.CharField(max_length=255, blank=True)


class Study(models.Model):
    team = models.ManyToManyField(User, related_name='study_team', null=True, blank=True)
    investigation = models.ForeignKey(Investigation, null=False, blank=False, on_delete=models.CASCADE)
    unique_id = models.CharField(max_length=255, unique=True, blank=True)
    title = models.CharField(max_length=250, blank=False)
    description = models.TextField(blank=True)
    start_date = models.DateField(default=timezone.now, blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    contact_institution = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    site_name = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    altitude = models.BigIntegerField(blank=True, null=True)
    altitude_units = models.CharField(max_length=20, blank=True, null=True)
    experimental_design_description = models.TextField(blank=True, null=True)
    experimental_design_type = models.CharField(max_length=255, blank=True, null=True)
    experimental_design_map = models.CharField(max_length=255, blank=True, null=True)
    observation_unit_level_hierarchy = models.CharField(max_length=255, blank=True, null=True)
    observation_unit_description = models.TextField(blank=True, null=True)
    growth_facility_description = models.TextField(blank=True, null=True)
    growth_facility_type = models.CharField(max_length=255, blank=True, null=True)
    cultural_practices = models.TextField(blank=True, null=True)
    dataset_paths = ArrayField(models.CharField(max_length=250), blank=True, null=True)


class DataFile(models.Model):
    path: str = models.CharField(max_length=1000, blank=True)
    description: str = models.TextField(blank=True)
    version: int = models.IntegerField(default=1, blank=True, null=True)
    checksum: str = models.CharField(max_length=32, blank=True)


class BiologicalMaterial(models.Model):
    unique_id = models.CharField(max_length=255, unique=True, blank=True)
    organism = models.CharField(max_length=255, unique=True, blank=True)
    genus = models.CharField(max_length=255, blank=True)
    species = models.CharField(max_length=255, blank=True)
    infraspecific_name = models.TextField(blank=True)
    latitude = models.DecimalField(blank=True, null=True, decimal_places=10, max_digits=10)
    longitude = models.DecimalField(blank=True, null=True, decimal_places=10, max_digits=10)
    altitude = models.DecimalField(blank=True, null=True, decimal_places=10, max_digits=10)
    coordinates_uncertainy = models.DecimalField(blank=True, null=True, decimal_places=10, max_digits=10)
    preprocessing = models.TextField(blank=True)
    source_id = models.CharField(max_length=255, blank=True)
    source_doi = models.CharField(max_length=255, blank=True)
    source_latitude = models.DecimalField(blank=True, null=True, decimal_places=10, max_digits=10)
    source_longitude = models.DecimalField(blank=True, null=True, decimal_places=10, max_digits=10)
    source_altitude = models.DecimalField(blank=True, null=True, decimal_places=10, max_digits=10)
    source_coordinates_uncertainy = models.DecimalField(blank=True, null=True, decimal_places=10, max_digits=10)
    source_description = models.TextField(blank=True)


class EnvironmentParameter(models.Model):
    name = models.TextField(blank=True)
    value = models.TextField(blank=True)


class ExperimentalFactor(models.Model):
    type = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    values = models.TextField(blank=True)


class Event(models.Model):
    type = models.CharField(max_length=255, blank=True)
    accession_number = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    date = models.DateField(default=timezone.now, blank=True, null=True)


class ObservationUnit(models.Model):
    unique_id = models.CharField(max_length=255, unique=True, blank=True)
    type = models.CharField(max_length=255, blank=True)
    external_id = models.CharField(max_length=255, blank=True)
    spatial_distribution = models.TextField(blank=True)
    factor_value = models.TextField(blank=True)


class Sample(models.Model):
    unique_id = models.CharField(max_length=255, unique=True, blank=True)
    structure_development_stage = models.CharField(max_length=255, blank=True)
    anatomical_entity = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    collection_date = models.DateField(default=timezone.now, blank=True, null=True)
    external_id = models.CharField(max_length=255, blank=True)


class ObservedVariable(models.Model):
    unique_id = models.CharField(max_length=255, unique=True, blank=True)
    name = models.CharField(max_length=255, blank=True)
    accession_number = models.CharField(max_length=255, blank=True)
    trait = models.CharField(max_length=255, blank=True)
    trait_accession_number = models.CharField(max_length=255, blank=True)
    method = models.CharField(max_length=255, blank=True)
    method_accession_number = models.CharField(max_length=255, blank=True)
    method_description = models.TextField(blank=True)
    method_reference = models.CharField(max_length=255, blank=True)
    scale = models.CharField(max_length=255, blank=True)
    scale_accession_number = models.CharField(max_length=255, blank=True)
    time_scale = models.CharField(max_length=255, blank=True)