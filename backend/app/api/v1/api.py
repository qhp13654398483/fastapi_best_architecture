#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Query, Request

from backend.app.common.casbin_rbac import DependsRBAC
from backend.app.common.jwt import DependsJwtAuth
from backend.app.common.pagination import PageDepends, paging_data
from backend.app.common.response.response_schema import response_base
from backend.app.database.db_mysql import CurrentSession
from backend.app.schemas.api import GetAllApi, CreateApi, UpdateApi
from backend.app.services.api_service import ApiService

router = APIRouter()


@router.get('/{pk}', summary='获取接口详情', dependencies=[DependsJwtAuth])
async def get_api(pk: int):
    api = await ApiService.get(pk=pk)
    return response_base.success(data=api)


@router.get('', summary='（模糊条件）分页获取所有接口', dependencies=[DependsJwtAuth, PageDepends])
async def get_all_apis(
    db: CurrentSession,
    name: Annotated[str | None, Query()] = None,
    method: Annotated[str | None, Query()] = None,
    path: Annotated[str | None, Query()] = None,
):
    api_select = await ApiService.get_select(name=name, method=method, path=path)
    page_data = await paging_data(db, api_select, GetAllApi)
    return response_base.success(data=page_data)


@router.post('', summary='创建接口', dependencies=[DependsRBAC])
async def create_api(request: Request, obj: CreateApi):
    await ApiService.create(obj=obj, user_id=request.user.id)
    return response_base.success()


@router.put('/{pk}', summary='更新接口', dependencies=[DependsRBAC])
async def update_api(request: Request, pk: int, obj: UpdateApi):
    count = await ApiService.update(pk=pk, obj=obj, user_id=request.user.id)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete('', summary='（批量）删除接口', dependencies=[DependsRBAC])
async def delete_api(pk: Annotated[list[int], Query(...)]):
    count = await ApiService.delete(pk=pk)
    if count > 0:
        return response_base.success()
    return response_base.fail()
