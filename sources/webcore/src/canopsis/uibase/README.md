# Uibase Canopsis Brick

## Index

- [Description](#description)
- [Content](#content)
- [Installation](#installation)
- [Usage](#usage)
- [Continuous-integration](#continuous-integration)
- [Code-notes](#code-notes)
- [Additional-info](#additional-info)

## Description

Base UI application layer for Canopsis frontend

## Content



## Screenshots



## Installation

You need to clone the git repository and copy directory to Canopsis path

    $ su - canopsis
    $ brickmanager install uibase

Then, you need to enable the brick

    $ brickmanager enable uibase

You can see enabled bricks

    $ su - canopsis
    $ brickmanager list
    [u'core', u'uibase', u'monitoring', ..., **u'uibase'**]

## Usage

See [Howto](https://git.canopsis.net/canopsis-ui-bricks/uibase/blob/master/doc/index.rst)

## Continuous-Integration

### Tests



### Lint

Tested on commit : 74ab6f4.

| Target | Status | Log |
| ------ | ------ | --- |
| Lint   | :negative_squared_cross_mark: ERROR |  |


## Code-Notes

### TODOS

| File   | Note   |
|--------|--------|
| src/components/colpick/component.js | check to destroy colpick |
| src/components/classifieditemselector/component.js | fuzzy search |
| src/components/classifieditemselector/component.js | hover effect |
| src/components/classifieditemselector/component.js | use searchmethodsregistry instead of plain old static code |
| src/components/classifieditemselector/component.js | use searchmethodsregistry instead of plain old static code |
| src/components/classifieditemselector/component.js | use searchmethodsregistry instead of plain old static code |
| src/components/elementidselectorwithoptions/component.js | put this on a dedicated util |
| src/components/elementidselectorwithoptions/component.js | manage default values |
| src/components/elementidselectorwithoptions/component.js | stop using polymorphicTypeKey, use sourceMappingKeys instead |
| src/components/filefield/component.js | check if all the component property are still used, and refactor if needed |
| src/components/table/component.js |: clean this try/catch |
| src/components/actionfilter/component.js | not used yet |
| src/widgets/crudcontext/controller.js | temporarily removed create button |
| src/widgets/crudcontext/controller.js | check if useless or not |
| src/widgets/list/controller.js | check if useless or not |
| src/mixins/arraysearch.js | these checks should be asserts |
| src/mixins/contextarraysearch.js | these checks should be asserts |
| src/mixins/customsendevent.js | use an adapter for this |
| src/mixins/customsendevent.js | refactor into sub classes |
| src/mixins/responsivelist.js | check if still used |
| src/editors/editor-elementidselectorwithoptions.hbs | manage search in a dynamic way, as an editor property binding to a search method |
| src/editors/editor-elementidselectorwithoptions.hbs | make this doc viewable on the generated doc |
| src/forms/pbehavior/controller.js | search this value into schema |
| src/forms/pbehavior/controller.js | refactor the 20 lines below in an utility function "getEditorForAttr" |
| src/forms/pbehavior/controller.js | use the real schema, not the dict used to create it |
| src/forms/done/controller.js | search this value into schema |
| src/forms/done/controller.js | refactor the 20 lines below in an utility function "getEditorForAttr" |
| src/forms/done/controller.js | use the real schema, not the dict used to create it |


### FIXMES

| File   | Note   |
|--------|--------|
| src/components/dateinterval/component.js | destroy the Jquery plugin at willDestroyElement, and check for possible undestroyed event bindings |
| src/components/classifiedcrecordselector/component.js | is store destroyed? |
| src/widgets/uimaintabcollection/controller.js |: the factory "widgetbase" is a hack to make the canopsis rights reopen work. But it make the view "app_header" not working without the canopsis-rights brick |
| src/mixins/periodicrefresh.js | periodicrefresh deactivated in testing mode because it throws global failures |
| src/mixins/responsivelist.js | undefined |


## Additional-info

Minified version : 4 files (size: 500K)
Development version : 288 files (size: 1,8M)
