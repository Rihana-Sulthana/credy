from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserRegistrationSerializer
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from base64 import b64encode
import os
from .models import *
import requests
from functools import wraps
from django.db.models import Func, F, Count, Sum


# Create your views here.

@permission_classes((AllowAny,))
class UserRegistrationView(CreateAPIView):
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = serializer.instance
        return Response(response)


def retry(times):
    """
    Decorator to retry any functions 'times' times.
    """

    def retry_decorator(func):
        @wraps(func)
        def retried_function(*args, **kwargs):
            for i in range(times - 1):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    pass

            func(*args, **kwargs)

        return retried_function

    return retry_decorator


@api_view(['GET'])
@retry(5)
@permission_classes((IsAuthenticated,))
def get_movies(request):
    try:
        user = os.getenv('client')
        password = os.getenv('secret_key')
        headers = {
            "Authorization": "Basic {}".format(
                b64encode(bytes(f"{user}:{password}", "utf-8")).decode("ascii")
            )
        }

        r = requests.get('https://demo.credy.in/api/v1/maya/movies/', headers=headers)
        if r.status_code != 200:
            raise Exception

        return Response(r.json())
    except:
        return Response("Some Error Occured, Please try again later")


@permission_classes((IsAuthenticated,))
class CollectionView(APIView):

    def post(self, request):
        try:
            data = request.data
            movies = data['movies']
            user = request.user.id

            collection_obj = Collection.objects.update_or_create(
                description=data['description'],
                defaults={"user_id": user, "title": data['title']}
            )
            for movie in movies:
                genres = movie['genres'].split(',') if movie.get('genres') else []
                movie_obj = Movie.objects.update_or_create(description=movie['description'],
                                                           genres=genres,
                                                           defaults={"collection": collection_obj[0],
                                                                     "title": movie['title']})

            return Response({"collection_uuid": collection_obj[0].id})
        except Exception as e:
            return Response(e.args[0])

    def get(self, request, collection_uuid=None):
        try:
            user = request.user.id
            if collection_uuid:
                collections = Collection.objects.filter(id=collection_uuid).prefetch_related('movie_set')
            else:
                collections = Collection.objects.filter(user_id=user).prefetch_related('movie_set')
            data = []
            for collection in collections:
                collection_data = {}
                collection_data['title'] = collection.title
                collection_data['description'] = collection.description
                collection_data['uuid'] = collection.id
                collection_data['movies'] = []
                movies_set = collection.movie_set.filter(collection_id=collection.id)
                for movie in movies_set:
                    movie_data = {}
                    movie_data['title'] = movie.title
                    movie_data['description'] = movie.description
                    movie_data['genres'] = movie.genres
                    movie_data['uuid'] = movie.id
                    collection_data['movies'].append(movie_data)
                data.append(collection_data)

            if collection_uuid:
                resp = data[0]
            else:
                top_genres = list(Movie.objects.annotate(top=Func(F('genres'),
                                                                  function='unnest')).values_list('top',
                                                                                                  flat=True).annotate(
                    count=Count('id')).order_by('-count')[:3])
                resp = {"is_success": True, "collections": data, "genres": top_genres}

            return Response(resp)
        except Exception as e:
            return Response(e.args[0])

    def put(self, request, collection_uuid):
        try:
            data = request.data
            movies = data['movies']
            colletion = Collection.objects.update_or_create(
                title=data['title'],
                description=data['description'],
                defaults={"id": collection_uuid}
            )
            for movie in movies:
                try:
                    movie = Movie.objects.update_or_create(
                        description=movie['description'],
                        genres=movie['genres'],
                        defaults={"collection_id": collection_uuid, "title": movie['title']}
                    )
                except:
                    pass
            return Response("Updated Successfully")
        except Exception as e:
            return Response(e.args[0])

    def delete(self, request, collection_uuid):
        try:
            collection = Collection.objects.filter(id=collection_uuid).delete()
            return Response("Collection deleted successfully")

        except Exception as e:
            return Response(e.args[0])


@permission_classes((IsAuthenticated,))
class ServerRequestCount(APIView):

    def post(self, request):
        try:
            count_obj = UserRequestCount.objects.all().delete()
            return Response({"message": "request count reset successfully"})
        except Exception as e:
            return Response(e.args[0])

    def get(self, request):
        try:
            count = list(UserRequestCount.objects.annotate(count=Sum('request_count')).values_list('count', flat=True))
            return Response({"requests": count[0] if count else 0})
        except Exception as e:
            return Response(e.args[0])
