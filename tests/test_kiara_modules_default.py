#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `kiara_plugin.playground` package."""

import kiara_plugin.playground
import pytest  # noqa


def test_assert():

    assert kiara_plugin.playground.get_version() is not None
