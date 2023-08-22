/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Creator } from '../models/Creator';
import type { CreatorCreate } from '../models/CreatorCreate';
import type { CreatorPatch } from '../models/CreatorPatch';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class CreatorsService {

    /**
     * Get Me
     * @returns Creator Successful Response
     * @throws ApiError
     */
    public static getMeCreatorsMeGet(): CancelablePromise<Creator> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/creators/me',
            errors: {
                404: `Not found`,
            },
        });
    }

    /**
     * Patch Me
     * @param requestBody
     * @returns Creator Successful Response
     * @throws ApiError
     */
    public static patchMeCreatorsMePatch(
        requestBody: CreatorPatch,
    ): CancelablePromise<Creator> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/creators/me',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get By Id
     * @param id
     * @returns Creator Successful Response
     * @throws ApiError
     */
    public static getByIdCreatorsIdGet(
        id: string,
    ): CancelablePromise<Creator> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/creators/{id}',
            path: {
                'id': id,
            },
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Delete By Id
     * @param id
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteByIdCreatorsIdDelete(
        id: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/creators/{id}',
            path: {
                'id': id,
            },
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Create
     * @param requestBody
     * @returns Creator Successful Response
     * @throws ApiError
     */
    public static createCreatorsUpgradePost(
        requestBody: CreatorCreate,
    ): CancelablePromise<Creator> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/creators/upgrade',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

}
