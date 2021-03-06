# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from multiprocessing import Value

import dash_core_components as dcc
import dash_html_components as html
import dash_flow_example
import dash_dangerously_set_inner_html

from dash import BaseDashView, no_update
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate


class DashView(BaseDashView):
    def __init__(self, **kwargs):
        super(DashView, self).__init__(**kwargs)

        self.dash.config.routes_pathname_prefix = '/dash/{}/'.format(self.dash_name)
        self.dash.css.config.serve_locally = True
        self.dash.scripts.config.serve_locally = True

    def _dash_component_suites(self, request, *args, **kwargs):
        self.dash._generate_scripts_html()
        self.dash._generate_css_dist_html()

        return super(DashView, self)._dash_component_suites(request, *args, **kwargs)


class DashSimpleCallback(DashView):
    dash_name = 'dash01'
    dash_components = {dcc.__name__, html.__name__}

    call_count = Value('i', 0)

    def __init__(self, **kwargs):
        super(DashSimpleCallback, self).__init__(**kwargs)

        self.dash.layout = html.Div([
            dcc.Input(
                id='input',
                value='initial value'
            ),
            html.Div(
                html.Div([
                    1.5,
                    None,
                    'string',
                    html.Div(id='output-1')
                ])
            )
        ])

        self.dash.callback(Output('output-1', 'children'),
                           [Input('input', 'value')])(self.update_output)

    def update_output(self, value):
        self.call_count.value = self.call_count.value + 1

        return value


class DashWildcardCallback(DashView):
    dash_name = 'dash02'
    dash_components = {html.__name__, dcc.__name__}

    call_count = Value('i', 0)

    def __init__(self, **kwargs):
        super(DashWildcardCallback, self).__init__(**kwargs)

        self.dash.layout = html.Div([
            dcc.Input(
                id='input',
                value='initial value'
            ),
            html.Div(
                html.Div([
                    1.5,
                    None,
                    'string',
                    html.Div(id='output-1', **{'data-cb': 'initial value',
                                               'aria-cb': 'initial value'})
                ])
            )
        ])

        self.dash.callback(Output('output-1', 'data-cb'),
                           [Input('input', 'value')])(self.update_data)
        self.dash.callback(Output('output-1', 'children'),
                           [Input('output-1', 'data-cb')])(self.update_text)

    def update_data(self, value):
        self.call_count.value = self.call_count.value + 1

        return value

    def update_text(self, data):
        return data


class DashAbortedCallback(DashView):
    dash_name = 'dash03'
    dash_components = {html.__name__, dcc.__name__}

    initial_input = 'initial input'
    initial_output = 'initial output'

    callback1_count = Value('i', 0)
    callback2_count = Value('i', 0)

    def __init__(self, **kwargs):
        super(DashAbortedCallback, self).__init__(**kwargs)

        self.dash.layout = html.Div([
            dcc.Input(id='input', value=self.initial_input),
            html.Div(self.initial_output, id='output1'),
            html.Div(self.initial_output, id='output2'),
        ])

        self.dash.callback(Output('output1', 'children'),
                           [Input('input', 'value')])(self.callback1)
        self.dash.callback(Output('output2', 'children'),
                           [Input('output1', 'children')])(self.callback2)

    def callback1(self, value):
        self.callback1_count.value += 1
        if self.callback1_count.value > 2:
            return no_update
        raise PreventUpdate('testing callback does not update')
        return value

    def callback2(self, value):
        self.callback2_count.value += 1
        return value


class DashWildcardDataAttributes(DashView):
    dash_name = 'dash04'
    dash_components = {html.__name__}

    test_time = datetime.datetime(2012, 1, 10, 2, 3)
    test_date = datetime.date(test_time.year, test_time.month, test_time.day)

    def __init__(self, **kwargs):
        super(DashWildcardDataAttributes, self).__init__(**kwargs)

        self.dash.layout = html.Div([
            html.Div(
                id='inner-element',
                **{
                    'data-string': 'multiple words',
                    'data-number': 512,
                    'data-none': None,
                    'data-date': self.test_date,
                    'aria-progress': 5
                }
            )
        ], id='data-element')


class DashFlowComponent(DashView):
    dash_name = 'dash05'
    dash_components = {html.__name__, dash_flow_example.__name__}

    def __init__(self, **kwargs):
        super(DashFlowComponent, self).__init__(**kwargs)

        self.dash.layout = html.Div([
            dash_flow_example.ExampleReactComponent(
                id='react',
                value='my-value',
                label='react component'
            ),
            dash_flow_example.ExampleFlowComponent(
                id='flow',
                value='my-value',
                label='flow component'
            ),
            html.Hr(),
            html.Div(id='output')
        ])

        self.dash.callback(Output('output', 'children'),
                           [Input('react', 'value'),
                            Input('flow', 'value')])(self.display_output)

    def display_output(self, react_value, flow_value):
        return html.Div([
            'You have entered {} and {}'.format(react_value, flow_value),
            html.Hr(),
            html.Label('Flow Component Docstring'),
            html.Pre(dash_flow_example.ExampleFlowComponent.__doc__),
            html.Hr(),
            html.Label('React PropTypes Component Docstring'),
            html.Pre(dash_flow_example.ExampleReactComponent.__doc__),
            html.Div(id='waitfor')
        ])


class DashNoPropsComponent(DashView):
    dash_name = 'dash06'
    dash_components = {html.__name__, dash_dangerously_set_inner_html.__name__}

    def __init__(self, **kwargs):
        super(DashNoPropsComponent, self).__init__(**kwargs)

        self.dash.layout = html.Div([
            dash_dangerously_set_inner_html.DangerouslySetInnerHTML('''
                <h1>No Props Component</h1>
            ''')
        ])


class DashMetaTags(DashView):
    dash_name = 'dash07'
    dash_components = {html.__name__}

    metas = [
        {'name': 'description', 'content': 'my dash app'},
        {'name': 'custom', 'content': 'customized'},
    ]

    def __init__(self, **kwargs):
        super(DashMetaTags, self).__init__(dash_meta_tags=self.metas, **kwargs)

        self.dash.layout = html.Div(id='content')


class DashIndexCustomization(DashView):
    dash_name = 'dash08'
    dash_components = {html.__name__}

    def __init__(self, **kwargs):
        super(DashIndexCustomization, self).__init__(**kwargs)

        self.template_name = 'dash_index_customization.html'
        self.dash.layout = html.Div('Dash app', id='app')


class DashAssets(DashView):
    dash_name = 'dash09'
    dash_components = {html.__name__, dcc.__name__}
    template_name = 'dash_assets.html'

    dash_assets_folder = 'dynamic_dash/assets'
    dash_assets_ignore = '*ignored.*'

    def __init__(self, **kwargs):
        super(DashAssets, self).__init__(**kwargs)

        self.dash.layout = html.Div([html.Div(id='content'), dcc.Input(id='test')], id='layout')


class DashInvalidIndexString(DashView):
    dash_name = 'dash10'
    dash_components = {html.__name__}

    def __init__(self, **kwargs):
        super(DashInvalidIndexString, self).__init__(**kwargs)

        self.dash.layout = html.Div()


class DashExternalFilesInit(DashView):
    dash_name = 'dash11'
    dash_components = {html.__name__}

    js_files = [
        'https://www.google-analytics.com/analytics.js',
        {'src': 'https://cdn.polyfill.io/v2/polyfill.min.js'},
        {
            'src': 'https://cdnjs.cloudflare.com/ajax/libs/ramda/0.26.1/ramda.min.js',
            'integrity': 'sha256-43x9r7YRdZpZqTjDT5E0Vfrxn1ajIZLyYWtfAXsargA=',
            'crossorigin': 'anonymous'
        },
        {
            'src': 'https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.11/lodash.min.js',
            'integrity': 'sha256-7/yoZS3548fXSRXqc/xYzjsmuW3sFKzuvOCHd06Pmps=',
            'crossorigin': 'anonymous'
        }
    ]

    css_files = [
        'https://codepen.io/chriddyp/pen/bWLwgP.css',
        {
            'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
            'rel': 'stylesheet',
            'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
            'crossorigin': 'anonymous'
        }
    ]

    def __init__(self, **kwargs):
        super(DashExternalFilesInit, self).__init__(dash_external_scripts=self.js_files,
                                                    dash_external_stylesheets=self.css_files, **kwargs)

        self.template_name = 'dash_external_files_init.html'
        self.dash.layout = html.Div()


class DashFuncLayoutAccepted(DashView):
    dash_name = 'dash12'
    dash_components = {html.__name__}

    def __init__(self, **kwargs):
        super(DashFuncLayoutAccepted, self).__init__(**kwargs)

        def create_layout():
            return html.Div('Hello World')

        self.dash.layout = create_layout


class DashLateComponentRegister(DashView):
    dash_name = 'dash13'
    dash_components = {html.__name__, dcc.__name__}

    def __init__(self, **kwargs):
        super(DashLateComponentRegister, self).__init__(**kwargs)

        self.dash.layout = html.Div([
            html.Button('Click me to put a dcc', id='btn-insert'),
            html.Div(id='output')
        ])

        self.dash.callback(Output('output', 'children'),
                           [Input('btn-insert', 'n_clicks')])(self.update_output)

    def update_output(self, value):
        if value is None:
            raise PreventUpdate()

        return dcc.Input(id='inserted-input')


class DashMultiOutput(DashView):
    dash_name = 'dash14'
    dash_components = {html.__name__}

    def __init__(self, **kwargs):
        super(DashMultiOutput, self).__init__(**kwargs)
        self.dash.layout = html.Div([
            html.Button('OUTPUT', id='output-btn'),

            html.Table([
                html.Thead([
                    html.Tr([html.Th('Output 1'), html.Th('Output 2')])
                ]),
                html.Tbody([
                    html.Tr([html.Td(id='output1'), html.Td(id='output2')]),
                ])
            ]),

            html.Div(id='output3'),
            html.Div(id='output4'),
            html.Div(id='output5')
        ])

        self.dash.callback([Output('output1', 'children'), Output('output2', 'children')],
                           [Input('output-btn', 'n_clicks')],
                           [State('output-btn', 'n_clicks_timestamp')])(self.on_click)
        self.dash.callback(Output('output3', 'children'),
                           [Input('output-btn', 'n_clicks')])(self.dummy_callback)

    def on_click(self, n_clicks, n_clicks_timestamp):
        if n_clicks is None:
            raise PreventUpdate

        return n_clicks, n_clicks_timestamp

    def dummy_callback(self, n_clicks):
        """Dummy callback for DuplicateCallbackOutput test
        """
        if n_clicks is None:
            raise PreventUpdate

        return 'Output 3: {}'.format(n_clicks)

    def on_click_duplicate(self, n_clicks):
        if n_clicks is None:
            raise PreventUpdate

        return 'something else'

    def on_click_duplicate_multi(self, n_clicks):
        if n_clicks is None:
            raise PreventUpdate

        return 'something else'

    def on_click_same_output(self, n_clicks):
        return n_clicks

    def overlapping_multi_output(self, n_clicks):
        return n_clicks


class DashMultiOutputNoUpdate(DashView):
    dash_name = 'dash15'
    dash_components = {html.__name__}

    def __init__(self, **kwargs):
        super(DashMultiOutputNoUpdate, self).__init__(**kwargs)

        self.dash.layout = html.Div([
            html.Button('B', 'btn'),
            html.P('initial1', 'n1'),
            html.P('initial2', 'n2'),
            html.P('initial3', 'n3')
        ])

        self.dash.callback([Output('n1', 'children'), Output('n2', 'children'), Output('n3', 'children')],
                           [Input('btn', 'n_clicks')])(self.show_clicks)

    def show_clicks(self, n):
        # partial or complete cancelation of updates via no_update
        return [
            no_update if n and n > 4 else n,
            no_update if n and n > 2 else n,
            no_update
        ]


class DashNoUpdateChains(DashView):
    dash_name = 'dash16'
    dash_components = {html.__name__, dcc.__name__}

    def __init__(self, **kwargs):
        super(DashNoUpdateChains, self).__init__(**kwargs)

        self.dash.layout = html.Div([
            dcc.Input(id='a_in', value='a'),
            dcc.Input(id='b_in', value='b'),
            html.P('', id='a_out'),
            html.P('', id='a_out_short'),
            html.P('', id='b_out'),
            html.P('', id='ab_out')
        ])

        self.dash.callback([Output('a_out', 'children'), Output('a_out_short', 'children')],
                           [Input('a_in', 'value')])(self.a_out)
        self.dash.callback(Output('b_out', 'children'), [Input('b_in', 'value')])(self.b_out)

        self.dash.callback(Output('ab_out', 'children'),
                           [Input('a_out_short', 'children')],
                           [State('b_out', 'children')])(self.ab_out)

    def a_out(self, a):
        return (a, a if len(a) < 3 else no_update)

    def b_out(self, b):
        return b

    def ab_out(self, a, b):
        return a + ' ' + b


class DashWithCustomRenderer(DashView):
    dash_name = 'dash17'
    dash_components = {html.__name__, dcc.__name__}
    template_name = 'dash_with_custom_renderer.html'

    def __init__(self, **kwargs):
        super(DashWithCustomRenderer, self).__init__(**kwargs)

        self.dash.layout = html.Div([
            dcc.Input(id='input', value='initial value'),
            html.Div(
                html.Div([
                    html.Div(id='output-1'),
                    html.Div(id='output-pre'),
                    html.Div(id='output-post')
                ])
            )
        ])

        self.dash.callback(Output('output-1', 'children'), [Input('input', 'value')])(self.update_output)

    def update_output(self, value):
        return value


class DashModifiedResponse(DashView):
    dash_name = 'dash19'
    dash_components = {html.__name__, dcc.__name__}

    def __init__(self, **kwargs):
        super(DashModifiedResponse, self).__init__(**kwargs)

        self.dash.layout = html.Div([
            dcc.Input(id='input', value='ab'),
            html.Div(id='output')
        ])

        self.dash.callback(Output('output', 'children'),
                           [Input('input', 'value')])(self.update_output)

    def update_output(self, value):
        self.response.set_cookie('dash_cookie', value + ' - cookie')
        return value + ' - output'


class DashOutputInputInvalidCallback(DashView):
    dash_name = 'dash21'
    dash_components = {html.__name__}

    def __init__(self, **kwargs):
        super(DashOutputInputInvalidCallback, self).__init__(**kwargs)

        self.dash.layout = html.Div([
            html.Div('child', id='input-output'),
            html.Div(id='out')
        ])

    def failure(self, children):
        pass

    def failure2(self, children):
        pass


class DashCallbackDepTypes(DashView):
    dash_name = 'dash22'
    dash_components = {html.__name__}

    def __init__(self, **kwargs):
        super(DashCallbackDepTypes, self).__init__(**kwargs)

        self.dash.layout = html.Div([
            html.Div('child', id='in'),
            html.Div('state', id='state'),
            html.Div(id='out')
        ])

    def f(self, i):
        return i

    def f2(self, i):
        return i

    def f3(self, i):
        return i

    def f4(self, i):
        return i


class DashCallbackReturnValidation(DashView):
    dash_name = 'dash23'
    dash_components = {html.__name__}

    def __init__(self, **kwargs):
        super(DashCallbackReturnValidation, self).__init__(**kwargs)

        self.dash.layout = html.Div([
            html.Div(id='a'),
            html.Div(id='b'),
            html.Div(id='c'),
            html.Div(id='d'),
            html.Div(id='e'),
            html.Div(id='f')
        ])

        self.dash.callback(Output('b', 'children'), [Input('a', 'children')])(self.single)
        self.dash.callback([Output('c', 'children'), Output('d', 'children')],
                           [Input('a', 'children')])(self.multi)
        self.dash.callback([Output('e', 'children'), Output('f', 'children')],
                           [Input('a', 'children')])(self.multi2)

    def single(self, a):
        return set([1])

    def multi(self, a):
        return [1, set([2])]

    def multi2(self, a):
        return ['abc']


class DashCallbackContext(DashView):
    dash_name = 'dash24'
    dash_components = {html.__name__}

    btns = ['btn-{}'.format(x) for x in range(1, 6)]

    def __init__(self, **kwargs):
        super(DashCallbackContext, self).__init__(**kwargs)

        self.dash.layout = html.Div([
            html.Div([html.Button(btn, id=btn) for btn in self.btns]),
            html.Div(id='output'),
        ])

        self.dash.callback(Output('output', 'children'),
                           [Input(x, 'n_clicks') for x in self.btns])(self.on_click)

    def on_click(self, *args):
        if not callback_context.triggered:
            raise PreventUpdate

        trigger = callback_context.triggered[0]
        return 'Just clicked {} for the {} time!'.format(
            trigger['prop_id'].split('.')[0], trigger['value']
        )
