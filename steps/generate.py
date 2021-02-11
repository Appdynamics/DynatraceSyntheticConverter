import os

import js2py
import glob
import json
from pathlib import Path
import logging


def generateScripts():
    if not os.path.exists('output'):
        os.makedirs('output')
    for file in glob.iglob('input/*.json'):
        filename = Path(file).stem
        schema = json.loads(open(file).read())
        if schema['type'] == 'clickpath':
            logging.info(f'Converting {filename}')

            events = schema['events']
            code = open('resources/conversionSnippets/base.txt').read()
            eventsCode = ''

            hasUnsupportedElements = False
            for event in events:
                if event['type'] == 'navigate':
                    eventsCode += genNavigateCode(event)
                elif event['type'] == 'keystrokes':
                    eventsCode += genKeystrokesCode(event)
                elif event['type'] == 'click':
                    eventsCode += genClickCode(event)
                elif event['type'] == 'javascript':
                    eventsCode += genJsToPythonCode(event)
                else:
                    hasUnsupportedElements = True
                    logging.debug(f'{event["type"]} is not yet supported')

            if hasUnsupportedElements:
                logging.info(f'{filename} not fully converted, contains unsupported elements')

            code = code.replace('# $EVENT_STEPS', eventsCode)

            with open(f'output/{Path(file).stem}.py', 'w') as outfile:
                logging.debug(f'Saving {filename}')
                outfile.write(code)
        else:
            logging.error(f'Schema type {schema["type"]} for {filename} is not supported. Skipping...')


def genNavigateCode(event) -> str:
    url = event['url']
    description = event['description']
    code = open('resources/conversionSnippets/navigate.txt').read() \
        .replace('$URL', url) \
        .replace('$DESCRIPTION', description)
    return code


def genKeystrokesCode(event):
    # next event target locator where the type is css and value contains a #, else grab the firtst one
    locators = event['target']['locators']
    locator = next((locator for locator in locators if locator['type'] == 'css' and '#' in locator['value']), locators[0])
    selector = locator['value'].replace("\"", "\\\"")
    keys = event['textValue']
    description = event['description']
    code = open('resources/conversionSnippets/keystrokes.txt').read() \
        .replace('$CSS_SELECTOR', selector) \
        .replace('$KEYS', keys) \
        .replace('$DESCRIPTION', description)
    return code


def genClickCode(event):
    locators = event['target']['locators']
    locator = next((locator for locator in locators if locator['type'] == 'css' and '#' in locator['value']),
                   locators[0])
    selector = locator['value'].replace("\"", "\\\"")
    description = event['description']
    code = open('resources/conversionSnippets/click.txt').read() \
        .replace('$CSS_SELECTOR', selector) \
        .replace('$DESCRIPTION', description)
    return code


def genJsToPythonCode(event):
    description = event['description']
    # this works but not really
    # with open(f'output/jsGen/tmp.js', 'w') as outfile:
    #     strippedJS = "".join([s for s in event['javaScript'].strip().splitlines(True) if s.strip()])
    #     outfile.write(strippedJS)
    # js2py.translate_file('output/jsGen/tmp.js', 'output/jsGen/tmp.py')
    # pythonCode = open('output/jsGen/tmp.py').read() \
    #         .replace('\n', '\n        ')
    pythonCode = '# TODO: Implement by hand'
    code = open('resources/conversionSnippets/pythonCode.txt').read() \
        .replace('$DESCRIPTION', description) \
        .replace('$PYTHON_CODE', pythonCode)
    return code
