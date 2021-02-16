import os
import re

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
    # next event target locator where the type is css and value contains a #, else grab the first one
    locators = event['target']['locators']
    selector = selectorFromLocators(locators)
    keys = event['textValue']
    description = event['description']
    code = open('resources/conversionSnippets/keystrokes.txt').read() \
        .replace('$SELECTOR', selector) \
        .replace('$KEYS', keys) \
        .replace('$DESCRIPTION', description)
    return code


def genClickCode(event):
    locators = event['target']['locators']
    selector = selectorFromLocators(locators)
    description = event['description']
    code = open('resources/conversionSnippets/click.txt').read() \
        .replace('$SELECTOR', selector) \
        .replace('$DESCRIPTION', description)
    return code


def selectorFromLocators(locators):
    cssIdLocator = \
        next((locator for locator in locators if locator['type'] == 'css' and '#' in locator['value']), None)
    if cssIdLocator is not None:
        cssID = cssIdLocator['value'].replace("\"", "\\\"")
        return f'driver.find_element_by_css_selector("{cssID}")'

    cssContainsLocator = \
        next((locator for locator in locators if locator['type'] == 'css' and 'contains' in locator['value']), None)
    if cssContainsLocator is not None:
        val = cssContainsLocator['value']
        content = re.search(r'\((.*)\)', val).group(1).replace("\"", "\\\"")
        tag = val.split(':')[0]
        return f'driver.find_element_by_xpath("//{tag}[contains(text(), {content})]")'

    cssDomNameLocator = \
        next((locator for locator in locators if locator['type'] == 'dom' and 'getElementsByName' in locator['value']),
             None)
    if cssDomNameLocator is not None:
        val = cssDomNameLocator['value']
        content = re.search(r'\((.*)\)', val).group(1).replace("\"", "\\\"")
        return f'driver.find_element_by_name("Submit")'

    return locators[0]['value'].replace("\"", "\\\"")


def genJsToPythonCode(event):
    description = event['description']
    code = open('resources/conversionSnippets/jsCode.txt').read() \
        .replace('$DESCRIPTION', description) \
        .replace('$JS_CODE', event['javaScript'].replace('\n', '\t\t'))
    return code
