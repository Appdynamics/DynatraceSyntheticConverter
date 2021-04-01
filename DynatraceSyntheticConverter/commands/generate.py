import os
import re

from click import command

import glob
import json
from pathlib import Path
import logging

CONVERSION_SNIPPET_BASE = 'DynatraceSyntheticConverter/resources/conversionSnippets/'


@command(
    name='generate',
    help='''
    Generate python scripts from Dynatrace synthetic monitor JSON.
    Generated scripts are placed in the output directory and will overwrite existing scripts of the same name.  
    ''')
def generate():
    logging.info(f'-----Launching generate step-----')

    if not os.path.exists('output'):
        os.makedirs('output')

    for file in glob.iglob('input/*.json'):
        filename = Path(file).stem
        schema = json.loads(open(file).read())
        if schema['type'] == 'clickpath':
            logging.info(f'Converting {filename}')

            events = schema['events']
            code = open(CONVERSION_SNIPPET_BASE + 'base.txt').read()
            eventsCode = ''

            hasUnsupportedElements = False
            for event in events:
                if event['type'] == 'navigate':
                    eventsCode += __genNavigateCode(event)
                elif event['type'] == 'keystrokes':
                    eventsCode += __genKeystrokesCode(event)
                elif event['type'] == 'click':
                    eventsCode += __genClickCode(event)
                elif event['type'] == 'javascript':
                    eventsCode += __genJsCode(event)
                elif event['type'] == 'selectOption':
                    eventsCode += __genSelectOptionCode(event)
                else:
                    hasUnsupportedElements = True
                    logging.debug(f'{event["type"]} is not yet supported')
                if 'validate' in event:
                    eventsCode += __genTextMatchCode(event)

            if hasUnsupportedElements:
                logging.info(f'{filename} not fully converted, contains unsupported elements')

            # trim trailing newline when we append our events code
            code = code.replace('# $EVENT_STEPS', eventsCode[:-1])

            with open(f'output/{Path(file).stem}.py', 'w') as outfile:
                logging.debug(f'Saving {filename}')
                outfile.write(code)
        else:
            logging.error(f'Schema type {schema["type"]} for {filename} is not supported. Skipping...')


def __genNavigateCode(event) -> str:
    url = event['url']
    description = event['description']
    code = open(CONVERSION_SNIPPET_BASE + 'actions/navigate.txt').read() \
        .replace('$URL', url) \
        .replace('$DESCRIPTION', description)
    return code


def __genKeystrokesCode(event):
    # next event target locator where the type is css and value contains a #, else grab the first one
    locators = event['target']['locators']
    selector = __selectorFromLocators(locators)
    keys = event['textValue']
    description = event['description']
    code = open(CONVERSION_SNIPPET_BASE + 'actions/keystrokes.txt').read() \
        .replace('$SELECTOR_TYPE', selector['selectorType']) \
        .replace('$SELECTOR_STRING', selector['selectorString']) \
        .replace('$KEYS', keys) \
        .replace('$DESCRIPTION', description)
    return code


def __genClickCode(event):
    locators = event['target']['locators']
    selector = __selectorFromLocators(locators)
    description = event['description']
    code = open(CONVERSION_SNIPPET_BASE + 'actions/click.txt').read() \
        .replace('$SELECTOR_TYPE', selector['selectorType']) \
        .replace('$SELECTOR_STRING', selector['selectorString']) \
        .replace('$DESCRIPTION', description)
    return code


def __genSelectOptionCode(event):
    locators = event['target']['locators']
    selector = __selectorFromLocators(locators)
    description = event['description']
    selections = event['selections'][0]['index']  # TODO: this'll not work for multi selects
    code = open(CONVERSION_SNIPPET_BASE + 'actions/selectOption.txt').read() \
        .replace('$SELECTOR_TYPE', selector['selectorType']) \
        .replace('$SELECTOR_STRING', selector['selectorString']) \
        .replace('$DESCRIPTION', description) \
        .replace('$INDEX', str(selections))
    return code


def __genTextMatchCode(event):
    code = ""
    for validator in event['validate']:
        if validator['type'] == 'content_match' or validator['type'] == 'text_match':
            if validator['failIfFound']:
                code += open(CONVERSION_SNIPPET_BASE + 'validators/textMatchFailIfFound.txt').read()
            else:
                code += open(CONVERSION_SNIPPET_BASE + 'validators/textMatchFailIfNotFound.txt').read()
            code = code.replace('$TEXT', validator['match'])
        if validator['type'] == 'element_match':
            locators = validator['target']['locators']
            selector = __selectorFromLocators(locators)
            if validator['failIfFound']:
                code += open(
                    CONVERSION_SNIPPET_BASE + 'validators/elementMatchFailIfFound.txt').read()
            else:
                code += open(CONVERSION_SNIPPET_BASE + 'validators/elementMatchFailIfNotFound.txt').read()
            code = code.replace('$SELECTOR_TYPE', selector['selectorType']) \
                .replace('$SELECTOR_STRING', selector['selectorString'])
    return code


def __genJsCode(event):
    description = event['description']
    code = open(CONVERSION_SNIPPET_BASE + 'actions/jsCode.txt').read() \
        .replace('$DESCRIPTION', description) \
        .replace('$JS_CODE', event['javaScript'].replace('\n', '\t\t'))
    return code


def __selectorFromLocators(locators):
    cssIdLocator = \
        next((locator for locator in locators if locator['type'] == 'css' and 'contains' not in locator['value']), None)
    if cssIdLocator is not None:
        cssID = cssIdLocator['value'].replace("\"", "\\\"")
        return {
            'selectorType': 'By.CSS_SELECTOR',
            'selectorString': cssID
        }

    cssContainsLocator = \
        next((locator for locator in locators if locator['type'] == 'css' and 'contains' in locator['value']), None)
    if cssContainsLocator is not None:
        val = cssContainsLocator['value']
        content = re.search(r'\((.*)\)', val).group(1).replace("\"", "\\\"")
        tag = val.split(':')[0]
        return {
            'selectorType': 'By.XPATH',
            'selectorString': f"//{tag}[contains(text(), {content})]"
        }

    cssDomNameLocator = \
        next((locator for locator in locators if locator['type'] == 'dom' and 'getElementsByName' in locator['value']),
             None)
    if cssDomNameLocator is not None:
        val = cssDomNameLocator['value']
        content = re.search(r'\((.*)\)', val).group(1)

        return {
            'selectorType': 'By.NAME',
            'selectorString': content
        }

    return 'None  # TODO: locator found is ' + locators[0]["value"].replace("\"", "\\\"")
