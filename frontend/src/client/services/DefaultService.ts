/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class DefaultService {

    /**
     * Health Check
     * @returns any Successful Response
     * @throws ApiError
     */
    public static healthCheckHealthGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/health',
        });
    }

    /**
     * Read Root
     * @returns any Successful Response
     * @throws ApiError
     */
    public static readRootGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/',
        });
    }

    /**
     * Read Item
     * @param itemId
     * @param q
     * @returns any Successful Response
     * @throws ApiError
     */
    public static readItemItemsItemIdGet(
        itemId: number,
        q?: (string | null),
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/items/{item_id}',
            path: {
                'item_id': itemId,
            },
            query: {
                'q': q,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Io Task
     * @returns any Successful Response
     * @throws ApiError
     */
    public static ioTaskIoTaskGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/io_task',
        });
    }

    /**
     * Cpu Task
     * @returns any Successful Response
     * @throws ApiError
     */
    public static cpuTaskCpuTaskGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/cpu_task',
        });
    }

    /**
     * Random Status
     * @returns any Successful Response
     * @throws ApiError
     */
    public static randomStatusRandomStatusGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/random_status',
        });
    }

    /**
     * Random Sleep
     * @returns any Successful Response
     * @throws ApiError
     */
    public static randomSleepRandomSleepGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/random_sleep',
        });
    }

    /**
     * Error Test
     * @returns any Successful Response
     * @throws ApiError
     */
    public static errorTestErrorTestGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/error_test',
        });
    }

}
