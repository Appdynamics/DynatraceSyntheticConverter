import responses

from DynatraceSyntheticConverter.api.appd.appd_service import AppDService


@responses.activate
def test_success():
    responses.add(method=responses.GET,
                  url='https://acme.saas.appdynamics.com:443/controller/rest/applications?output=json',
                  json={
                      'applicationName': 'foo'
                  },
                  status=200)
    controllerService = AppDService('acme.saas.appdynamics.com', 443, True, 'acme', 'bar', 'hunter1')
    result = controllerService.get_applications()

    assert result.error is None
    assert result.data['applicationName'] == 'foo'


@responses.activate
def test_failure():
    responses.add(method=responses.GET,
                  url='https://acme.saas.appdynamics.com:443/controller/rest/applications?output=json',
                  json={},
                  status=500)
    controllerService = AppDService('acme.saas.appdynamics.com', 443, True, 'acme', 'bar', 'hunter1')
    result = controllerService.get_applications()

    assert result.error.msg == 500
