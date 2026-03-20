from rest_framework.views import APIView
from rest_framework.response import Response
from ..services import get_video_info

class VideoInfoView(APIView):
    def get(self, request):
        url = request.GET.get("url")
        data = get_video_info(url)
        return Response(data)
