# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: calculator.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10\x63\x61lculator.proto\x12\ncalculator\"\x1f\n\x07Request\x12\t\n\x01\x61\x18\x01 \x01(\x05\x12\t\n\x01\x62\x18\x02 \x01(\x05\"\x1a\n\x08Response\x12\x0e\n\x06result\x18\x01 \x01(\x02\x32\xe9\x01\n\nCalculator\x12\x32\n\x03\x41\x64\x64\x12\x13.calculator.Request\x1a\x14.calculator.Response\"\x00\x12\x37\n\x08Subtract\x12\x13.calculator.Request\x1a\x14.calculator.Response\"\x00\x12\x37\n\x08Multiply\x12\x13.calculator.Request\x1a\x14.calculator.Response\"\x00\x12\x35\n\x06\x44ivide\x12\x13.calculator.Request\x1a\x14.calculator.Response\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'calculator_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _REQUEST._serialized_start=32
  _REQUEST._serialized_end=63
  _RESPONSE._serialized_start=65
  _RESPONSE._serialized_end=91
  _CALCULATOR._serialized_start=94
  _CALCULATOR._serialized_end=327
# @@protoc_insertion_point(module_scope)
