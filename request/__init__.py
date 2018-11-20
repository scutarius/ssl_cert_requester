from .requester import Requester

get = Requester.get
post = Requester.post
put = Requester.put
delete = Requester.delete

__all__ = ['get', 'post', 'put', 'delete']
