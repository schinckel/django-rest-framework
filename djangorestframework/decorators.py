import re

def etag(etag_generator):
    def decorate_method(method):
        def wrapper(self, request, *args, **kwargs):
            value = etag_generator(request, *args, **kwargs)
            self._ETAG = '"%s"' % value
            if request.method in ["GET", "HEAD"]:
                etags = re.split(r'\W*,\W*', request.META.get('HTTP_IF_NONE_MATCH', ''))
                if value in etags or '*' in etags:
                    raise ErrorResponse(status=304)
            elif request.method in ["PUT", "POST", "DELETE"]:
                etags = re.split(r'\W*,\W*', request.META.get('HTTP_IF_MATCH', ''))
                if value in etags or '*' in etags:
                    raise ErrorResponse(status=412)
            
            return method(self, request, *args, **kwargs)
        return wrapper
    return decorate_method

# Intended use:

# def etag_generator(request, pk):
#     return Foo.objects.get(pk=pk).updated_at
#

# class MyView(View):
#     @etag(etag_generator)
#     def get(self, request, pk):
#       # Complicated/lengthy processing which can be ignored if the
#       # most desired Foo has not changed/been edited.
#       return Foo.objects.get(pk=pk)
#
#     @etag(etag_generator)
#     def put(self, request, pk):
#         # This will only run if the object has not changed.
#         Foo.objects.filter(pk=pk).update(**request.DATA)