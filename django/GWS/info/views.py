from django.shortcuts import render

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.throttling import AnonRateThrottle
from rest_framework.decorators import api_view, schema

from rest_framework import serializers
from utils.docstr_schema import DocstrSchema


class SnippetSerializer(serializers.Serializer):
    id = 123

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return {123}

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """

        return instance


class TestBrowsableAPI(generics.GenericAPIView):
    name = "test-browsable-api"
    throttle_classes = [AnonRateThrottle]
    schema = None
    serializer_class = SnippetSerializer

    def get(self, request, *args, **kwargs):
        return Response("test")


@api_view(["GET", "POST"])
@schema(None)
def hello_world(request):
    """
    get:
      description: delete log file by using get method
      summary: delete log file
      parameters:
        - name: file_path
          in: query
          description: file path of the log to delete
          schema:
            type: string
      responses:
        '200':
          description: log file deleted
          content:
            'application/json': {}
    post:
        bbbb:123
    """
    if request.method == "POST":
        return Response({"message": "Got some data!", "data": request.data})
    return Response({"message": "Hello, world!"})
