import responses

from DynatraceSyntheticConverter.api.appd.appd_service import AppDService


@responses.activate
def test_success():
    responses.add(method=responses.GET,
                  url='https://acme.saas.appdynamics.com:443/controller/auth?action=login',
                  json={},
                  headers={'Set-Cookie': 'JSESSIONID=foo; X-CSRF-TOKEN=bar;'},
                  status=200)
    controllerService = AppDService('acme.saas.appdynamics.com', 443, True, 'acme', 'bar', 'hunter1')
    result = controllerService.login_to_controller()

    assert result.error is None
    assert controllerService.controller.jsessionid == 'foo'
    assert controllerService.controller.xcsrftoken == 'bar'


@responses.activate
def test_no_jsessionid():
    responses.add(method=responses.GET,
                  url='https://acme.saas.appdynamics.com:443/controller/auth?action=login',
                  json={},
                  headers={'Set-Cookie': 'X-CSRF-TOKEN=bar;'},
                  status=200)
    controllerService = AppDService('acme.saas.appdynamics.com', 443, True, 'foo', 'bar', 'baz')
    result = controllerService.login_to_controller()

    assert result.error.msg == 'Valid authentication headers not cached from previous login call. Please verify credentials.'
    assert controllerService.controller.jsessionid is None
    assert controllerService.controller.xcsrftoken == 'bar'


@responses.activate
def test_no_xcsrftoken():
    responses.add(method=responses.GET,
                  url='https://acme.saas.appdynamics.com:443/controller/auth?action=login',
                  json={},
                  headers={'Set-Cookie': 'JSESSIONID=foo;'},
                  status=200)
    controllerService = AppDService('acme.saas.appdynamics.com', 443, True, 'foo', 'bar', 'baz')
    result = controllerService.login_to_controller()

    assert result.error.msg == 'Valid authentication headers not cached from previous login call. Please verify credentials.'
    assert controllerService.controller.jsessionid == 'foo'
    assert controllerService.controller.xcsrftoken == None


@responses.activate
def test_authentication_failure():
    responses.add(method=responses.GET,
                  url='https://acme.saas.appdynamics.com:443/controller/auth?action=login',
                  json={},
                  status=401)
    controllerService = AppDService('acme.saas.appdynamics.com', 443, True, 'foo', 'bar', 'baz')
    result = controllerService.login_to_controller()

    assert result.error.msg == 'Controller login failed with 401.'
