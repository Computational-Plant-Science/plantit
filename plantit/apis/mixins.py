'''
    Mixins used by multiple views within the REST API.
'''
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from django.core.exceptions import PermissionDenied


class PinViewMixin:
    '''
        Adds pin and unpin routes to a rest_framework.ModelViewSet.

        The plantit.user.models.Profile must have a many-to-many
        field linking the user profile to the model in the ModelViewSet's query,
        The field must have a `related="profile_pins"``

        Provides the following extra urls:
        - `[url to viewset]/<object pk>/pin`: Pin the object with the given pk to the user
        - `[url to viewset]/<object pk>/unpin`: Unpin the object with the given pk to the user

        Example:

            pinned_jobs = models.ManyToManyField(Job, related_name='profile_pins')

    '''
    @action(detail=True, methods=['post'])
    def pin(self, request, pk=None):
        """
            Mark a job as pinned.
        """
        obj = self.queryset.filter(user=request.user,pk=pk).first()
        obj.profile_pins.add(request.user.profile)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def unpin(self, request, pk=None):
        """
            Mark a job as unpinned.
        """
        obj = self.queryset.filter(user=request.user,pk=pk).first()
        obj.profile_pins.remove(request.user.profile)
        return Response(status=status.HTTP_200_OK)

class PinnedSerilizerMethodMixin:
    '''
        Provides the function to add a field to a
        sterilizer that shows if the model object is
        pinned by the user.

        The plantit.user.models.Profile must have a many-to-many
        field linking the user profile to the model in the ModelViewSet's query,
        The field must have a `related="profile_pins"``

        Example:
            pinned_jobs = models.ManyToManyField(Job, related_name='profile_pins')

        The serializer must have the following field:

        pinned = serializers.SerializerMethodField('pinnedByUser', source='profile_pins')
    '''
    def pinnedByUser(self, obj):
        '''
            Is the object pinned by the user.

            Args:
                obj: The object with a profile_pins field.

            Returns:
                True if the user has pinned the job, False otherwise.
        '''
        request = self.context.get('request', None)
        if request is not None:
            if(request.user.is_anonymous):
                #If data is being access via a token, no user info is available.
                return "N/A: Request did not originate from a user."
            else:
                return obj.profile_pins.filter(user=request.user).first() is not None
        else:
            raise PermissionDenied("Must be a request to access user data.")
