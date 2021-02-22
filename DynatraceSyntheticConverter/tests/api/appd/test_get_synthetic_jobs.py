import responses

from DynatraceSyntheticConverter.api.appd.appd_service import AppDService


@responses.activate
def test_success():
    responses.add(method=responses.GET,
                  url='https://acme.saas.appdynamics.com:443/controller/auth?action=login',
                  json={},
                  headers={'Set-Cookie': 'JSESSIONID=foo; X-CSRF-TOKEN=bar;'},
                  status=200)
    responses.add(method=responses.POST,
                  url='https://acme.saas.appdynamics.com:443/controller/restui/synthetic/schedule/getJobList/foo?output=json',
                  json={
                      'config': {
                          'script': 'foo',
                          'browserCodes': 'bar',
                          'locationCodes': 'baz',
                          'timeoutSeconds': 'foo',
                          'rate': {
                              'value': 'bar',
                              'unit': 'baz',
                          }
                      }
                  },
                  status=200)
    controllerService = AppDService('acme.saas.appdynamics.com', 443, True, 'acme', 'bar', 'hunter1')
    result = controllerService.get_synthetic_jobs('foo')

    assert result.error is None
    assert result.data['config']['script'] == 'foo'
    assert result.data['config']['browserCodes'] == 'bar'
    assert result.data['config']['locationCodes'] == 'baz'
    assert result.data['config']['timeoutSeconds'] == 'foo'
    assert result.data['config']['rate']['value'] == 'bar'
    assert result.data['config']['rate']['unit'] == 'baz'


@responses.activate
def test_failure():
    responses.add(method=responses.GET,
                  url='https://acme.saas.appdynamics.com:443/controller/auth?action=login',
                  json={},
                  headers={'Set-Cookie': 'JSESSIONID=foo; X-CSRF-TOKEN=bar;'},
                  status=200)
    responses.add(method=responses.POST,
                  url='https://acme.saas.appdynamics.com:443/controller/restui/synthetic/schedule/getJobList/foo?output=json',
                  json={},
                  status=500)
    controllerService = AppDService('acme.saas.appdynamics.com', 443, True, 'acme', 'bar', 'hunter1')
    result = controllerService.get_synthetic_jobs('foo')

    assert result.error.msg == 500


@responses.activate
def test_login_failure():
    responses.add(method=responses.GET,
                  url='https://acme.saas.appdynamics.com:443/controller/auth?action=login',
                  json={},
                  status=401)
    controllerService = AppDService('acme.saas.appdynamics.com', 443, True, 'acme', 'bar', 'hunter1')
    result = controllerService.get_synthetic_jobs('foo')

    assert result.error.msg == 'Controller login failed with 401.'
