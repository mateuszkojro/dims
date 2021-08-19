#!/bin/bash
jupyter nbconvert --execute $@ --to html # testing_common_trigger.ipynb#region_props.ipynb
jupyter nbconvert --execute $@ --to pdf #region_props.ipynb
