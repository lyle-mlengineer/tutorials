from fastapi import APIRouter, status

from .models import PlaylistUrl
from .utils import write_playlist_to_redis_queue

playlist_router = APIRouter(prefix="/playlists", tags=["Playlist"])


@playlist_router.post("/queue", status_code=status.HTTP_202_ACCEPTED)
async def queue_playlist_for_extraction(playlist_url: PlaylistUrl) -> None:
    write_playlist_to_redis_queue(playlist_url=playlist_url)
