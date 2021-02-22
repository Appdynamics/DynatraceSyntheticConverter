import responses

from DynatraceSyntheticConverter.api.dynatrace.dynatrace_service import DynatraceService


@responses.activate
def test_get_synthetic_monitors_success():
    responses.add(method=responses.GET,
                  url='https://foo.live.dynatrace.com/api/v1/synthetic/monitors',
                  json={
                      "monitors": [{
                          "entityId": "foo"
                      }, {
                          "entityId": "bar"
                      }]

                  },
                  status=200)
    dynatraceService = DynatraceService("https://foo.live.dynatrace.com", "foo")
    result = dynatraceService.get_synthetic_monitors()

    assert result.error is None
    assert len(result.data['monitors']) == 2
    assert result.data['monitors'][0]['entityId'] == 'foo'
    assert result.data['monitors'][1]['entityId'] == 'bar'


@responses.activate
def test_get_synthetic_monitors_failure():
    responses.add(method=responses.GET,
                  url='https://foo.live.dynatrace.com/api/v1/synthetic/monitors',
                  json={},
                  status=500)
    dynatraceService = DynatraceService("https://foo.live.dynatrace.com", "foo")
    result = dynatraceService.get_synthetic_monitors()

    assert result.error.msg == 500
