import falcon
import json
import logging

falcon_log = logging.getLogger('falcon')

class RequireJSON:
    def process_request(self, req, resp):
        if not req.client_accepts_json:
            falcon_log.exception('Error handling request with wrong format')
            raise falcon.HTTPNotAcceptable(
                'This API only supports responses encoded as JSON.')
        if req.method in ('POST',):
            if 'application/json' not in req.content_type:
                falcon_log.exception('Error handling request with wrong format')
                raise falcon.HTTPUnsupportedMediaType(
                    'This API only supports requests encoded as JSON.')


class JSONTranslator:
    # Retrieve your request JSON using req.context['doc']
    # Set your JSON response in req.context['result']

    def process_request(self, req, resp):
        if req.content_length in (None, 0):
            # Nothing to do
            return

        body = req.stream.read()
        if not body:
            falcon_log.exception('Empty request body')
            raise falcon.HTTPBadRequest('Empty request body',
                                        'A valid JSON document is required.')

        try:
            req.context['doc'] = json.loads(body.decode('utf-8'))

        except (ValueError, UnicodeDecodeError):
            falcon_log.exception('Malformed JSON, could not decode')
            raise falcon.HTTPError(falcon.HTTP_753,
                                   'Malformed JSON',
                                   'Could not decode the request body. The '
                                   'JSON was incorrect or not encoded as '
                                   'UTF-8.')

    def process_response(self, req, resp, resource):
        if 'result' not in req.context:
            return

        resp.body = json.dumps(req.context['result'], ensure_ascii=False, sort_keys=True)
