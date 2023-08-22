/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Tag } from '../models/Tag';
import type { TagCreate } from '../models/TagCreate';
import type { TagUpdate } from '../models/TagUpdate';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class TagsService {

    /**
     * Get Tags
     * @returns Tag Successful Response
     * @throws ApiError
     */
    public static getTagsTagsGet(): CancelablePromise<Array<Tag>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/tags/',
            errors: {
                404: `Not found`,
            },
        });
    }

    /**
     * Create Tag
     * @param requestBody
     * @returns Tag Successful Response
     * @throws ApiError
     */
    public static createTagTagsPost(
        requestBody: TagCreate,
    ): CancelablePromise<Tag> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/tags/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Tag By Id
     * @param tagId
     * @returns Tag Successful Response
     * @throws ApiError
     */
    public static getTagByIdTagsTagIdGet(
        tagId: number,
    ): CancelablePromise<Tag> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/tags/{tag_id}',
            path: {
                'tag_id': tagId,
            },
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Delete Tag
     * @param tagId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteTagTagsTagIdDelete(
        tagId: number,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/tags/{tag_id}',
            path: {
                'tag_id': tagId,
            },
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Patch Tag
     * @param tagId
     * @param requestBody
     * @returns Tag Successful Response
     * @throws ApiError
     */
    public static patchTagTagsTagIdPatch(
        tagId: number,
        requestBody: TagUpdate,
    ): CancelablePromise<Tag> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/tags/{tag_id}',
            path: {
                'tag_id': tagId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

}
