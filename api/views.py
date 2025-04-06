from django.shortcuts import render
from rest_framework import viewsets, status
from .models import Meal, Rating
from .serializers import MealSerializer, RatingSerializer, UserSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import RatingSerializer

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser,IsAuthenticatedOrReadOnly
from rest_framework.authtoken.models import Token


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    authentication_classes = (TokenAuthentication, )
    permission_classes = (AllowAny, )

    # Only allow POST (create) method
    http_method_names = ['post']


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data= request.data)
        serializer.is_valid(raise_exception=True)
        # user = serializer.save() #same as below
        self.perform_create(serializer) #it make >>> serializer.save()

        # get_or_create() or create() just a quary function
        token, created = Token.objects.get_or_create(user=serializer.instance)
        return Response({
            'token':token.key
        },
        status=status.HTTP_201_CREATED)

    # we will stop list() , retrieve() , update() , partial_update() , destroy() actions for authentication and security
    # we override methods below
    # def list(self, request, *args, **kwargs):
    #     return Response({'message': 'Listing users is not allowed'}, status=status.HTTP_403_FORBIDDEN)

    # def retrieve(self, request, *args, **kwargs):
    #     return Response({'message': 'Retrieving users is not allowed'}, status=status.HTTP_403_FORBIDDEN)

    # def update(self, request, *args, **kwargs):
    #     return Response({'message': 'Updating users is not allowed'}, status=status.HTTP_403_FORBIDDEN)

    # def partial_update(self, request, *args, **kwargs):
    #     return Response({'message': 'Partial updates are not allowed'}, status=status.HTTP_403_FORBIDDEN)

    # def destroy(self, request, *args, **kwargs):
    #     return Response({'message': 'Deleting users is not allowed'}, status=status.HTTP_403_FORBIDDEN)





class MealViewSet(viewsets.ModelViewSet):
    queryset = Meal.objects.all()
    serializer_class = MealSerializer

    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    # make additons to create and update rating from meal using decorator (@action)
    # !!! not best practice to write on views for preformance 
    @action(detail=True, methods=['POST'])
    def rate_meal(self, request, pk=None):
        if 'stars' in request.data:

            meal = Meal.objects.get(id = pk)
            stars = request.data['stars']
            user = request.user # to use token instead of below

            # username = request.data['username'] 
            # user = User.objects.get(username=username)

            try:
                # update
                rating = Rating.objects.get(user=user.id, meal=meal.id)
                rating.stars = stars
                rating.save()
                serializer = RatingSerializer(rating, many=False)
                json ={
                    'message' : 'Meal Rate Update',
                    'result' : serializer.data
                }

                return Response(json , status= status.HTTP_202_ACCEPTED)
            
            except:
                # create
                rating = Rating.objects.create(stars=stars, meal=meal, user=user)
                serializer = RatingSerializer(rating, many=False)
                json = {
                    'message' : 'Meal Rate Created',
                    'result' : serializer.data
                }
                return Response(json , status= status.HTTP_200_OK)

        else:
            json = {
                'message' : 'stars not provided'
            }
            return Response(json , status= status.HTTP_400_BAD_REQUEST)

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    authantication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def update(self, request ,*args, **kwargs):
        response = {
            'message': 'Invalid way to create or update',
        }
        return response(response, status=status.HTTP_400_BAD_REQUEST)
    def create(self, request ,*args, **kwargs):
        response = {
            'message': 'Invalid way to create or update',
        }
        return response(response, status=status.HTTP_400_BAD_REQUEST)