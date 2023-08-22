/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Clone } from '../models/Clone';
import type { CloneCreate } from '../models/CloneCreate';
import type { CloneSearchResult } from '../models/CloneSearchResult';
import type { CloneSortType } from '../models/CloneSortType';
import type { CloneUpdate } from '../models/CloneUpdate';
import type { Document } from '../models/Document';
import type { DocumentCreate } from '../models/DocumentCreate';
import type { DocumentUpdate } from '../models/DocumentUpdate';
import type { LongDescription } from '../models/LongDescription';
import type { Monologue } from '../models/Monologue';
import type { MonologueCreate } from '../models/MonologueCreate';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class ClonesService {

    /**
     * Create Clone
     * @param requestBody
     * @returns Clone Successful Response
     * @throws ApiError
     */
    public static createCloneClonesPost(
        requestBody: CloneCreate,
    ): CancelablePromise<Clone> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/clones/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Query Clones
     * @param tags
     * @param name
     * @param sort
     * @param similar
     * @param createdAfter
     * @param createdBefore
     * @param offset
     * @param limit
     * @returns CloneSearchResult Successful Response
     * @throws ApiError
     */
    public static queryClonesClonesGet(
        tags?: (Array<number> | null),
        name?: (string | null),
        sort?: CloneSortType,
        similar?: (string | null),
        createdAfter?: (string | null),
        createdBefore?: (string | null),
        offset?: number,
        limit: number = 10,
    ): CancelablePromise<Array<CloneSearchResult>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/clones/',
            query: {
                'tags': tags,
                'name': name,
                'sort': sort,
                'similar': similar,
                'created_after': createdAfter,
                'created_before': createdBefore,
                'offset': offset,
                'limit': limit,
            },
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Clone By Id
     * @param cloneId Clone ID
     * @returns Clone Successful Response
     * @throws ApiError
     */
    public static getCloneByIdClonesCloneIdGet(
        cloneId: string,
    ): CancelablePromise<Clone> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/clones/{clone_id}',
            path: {
                'clone_id': cloneId,
            },
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Patch Clone
     * @param cloneId Clone ID
     * @param requestBody
     * @returns Clone Successful Response
     * @throws ApiError
     */
    public static patchCloneClonesCloneIdPatch(
        cloneId: string,
        requestBody: CloneUpdate,
    ): CancelablePromise<Clone> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/clones/{clone_id}',
            path: {
                'clone_id': cloneId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Delete
     * @param cloneId Clone ID
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteClonesCloneIdDelete(
        cloneId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/clones/{clone_id}',
            path: {
                'clone_id': cloneId,
            },
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Generate Long Desc
     * @param cloneId
     * @returns LongDescription Successful Response
     * @throws ApiError
     */
    public static generateLongDescClonesCloneIdGenerateLongDescriptionPost(
        cloneId: string,
    ): CancelablePromise<LongDescription> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/clones/{clone_id}/generate_long_description',
            path: {
                'clone_id': cloneId,
            },
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * View Generated Long Descs
     * @param cloneId
     * @returns LongDescription Successful Response
     * @throws ApiError
     */
    public static viewGeneratedLongDescsClonesCloneIdLongDescriptionsGet(
        cloneId: string,
    ): CancelablePromise<Array<LongDescription>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/clones/{clone_id}/long_descriptions',
            path: {
                'clone_id': cloneId,
            },
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Create Document
     * @param cloneId
     * @param requestBody
     * @returns Document Successful Response
     * @throws ApiError
     */
    public static createDocumentClonesCloneIdDocumentsPost(
        cloneId: string,
        requestBody: DocumentCreate,
    ): CancelablePromise<Document> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/clones/{clone_id}/documents',
            path: {
                'clone_id': cloneId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Documents
     * @param cloneId
     * @param offset
     * @param limit
     * @param description
     * @param name
     * @param createdAfter
     * @param createdBefore
     * @returns Document Successful Response
     * @throws ApiError
     */
    public static getDocumentsClonesCloneIdDocumentsGet(
        cloneId: string,
        offset?: number,
        limit: number = 10,
        description?: (string | null),
        name?: (string | null),
        createdAfter?: (string | null),
        createdBefore?: (string | null),
    ): CancelablePromise<Array<Document>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/clones/{clone_id}/documents',
            path: {
                'clone_id': cloneId,
            },
            query: {
                'offset': offset,
                'limit': limit,
                'description': description,
                'name': name,
                'created_after': createdAfter,
                'created_before': createdBefore,
            },
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Update Document
     * @param documentId Document ID
     * @param cloneId
     * @param requestBody
     * @returns Document Successful Response
     * @throws ApiError
     */
    public static updateDocumentClonesCloneIdDocumentsDocumentIdPatch(
        documentId: string,
        cloneId: string,
        requestBody: DocumentUpdate,
    ): CancelablePromise<Document> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/clones/{clone_id}/documents/{document_id}',
            path: {
                'document_id': documentId,
                'clone_id': cloneId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Delete Document
     * @param documentId Document ID
     * @param cloneId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteDocumentClonesCloneIdDocumentsDocumentIdDelete(
        documentId: string,
        cloneId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/clones/{clone_id}/documents/{document_id}',
            path: {
                'document_id': documentId,
                'clone_id': cloneId,
            },
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Document By Id
     * @param cloneId
     * @param documentId Document ID
     * @returns Document Successful Response
     * @throws ApiError
     */
    public static getDocumentByIdClonesCloneIdDocumentsDocumentIdGet(
        cloneId: string,
        documentId: string,
    ): CancelablePromise<Document> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/clones/{clone_id}/documents/{document_id}',
            path: {
                'clone_id': cloneId,
                'document_id': documentId,
            },
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Update Monologue
     * @param monologueId Monologue ID
     * @param cloneId
     * @param requestBody
     * @returns Monologue Successful Response
     * @throws ApiError
     */
    public static updateMonologueClonesCloneIdMonologuesMonologueIdPatch(
        monologueId: string,
        cloneId: string,
        requestBody: DocumentUpdate,
    ): CancelablePromise<Monologue> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/clones/{clone_id}/monologues/{monologue_id}',
            path: {
                'monologue_id': monologueId,
                'clone_id': cloneId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Delete Monologue
     * @param monologueId Monologue ID
     * @param cloneId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteMonologueClonesCloneIdMonologuesMonologueIdDelete(
        monologueId: string,
        cloneId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/clones/{clone_id}/monologues/{monologue_id}',
            path: {
                'monologue_id': monologueId,
                'clone_id': cloneId,
            },
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Monologue By Id
     * @param cloneId
     * @param monologueId Monologue ID
     * @returns Monologue Successful Response
     * @throws ApiError
     */
    public static getMonologueByIdClonesCloneIdMonologuesMonologueIdGet(
        cloneId: string,
        monologueId: string,
    ): CancelablePromise<Monologue> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/clones/{clone_id}/monologues/{monologue_id}',
            path: {
                'clone_id': cloneId,
                'monologue_id': monologueId,
            },
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Create Monologue
     * @param cloneId
     * @param requestBody
     * @returns Monologue Successful Response
     * @throws ApiError
     */
    public static createMonologueClonesCloneIdMonologuesPost(
        cloneId: string,
        requestBody: Array<MonologueCreate>,
    ): CancelablePromise<Array<Monologue>> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/clones/{clone_id}/monologues',
            path: {
                'clone_id': cloneId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Monologues
     * @param cloneId
     * @param offset
     * @param limit
     * @param content
     * @param source
     * @param createdAfter
     * @param createdBefore
     * @returns Monologue Successful Response
     * @throws ApiError
     */
    public static getMonologuesClonesCloneIdMonologuesGet(
        cloneId: string,
        offset?: number,
        limit: number = 10,
        content?: (string | null),
        source?: (string | null),
        createdAfter?: (string | null),
        createdBefore?: (string | null),
    ): CancelablePromise<Array<Monologue>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/clones/{clone_id}/monologues',
            path: {
                'clone_id': cloneId,
            },
            query: {
                'offset': offset,
                'limit': limit,
                'content': content,
                'source': source,
                'created_after': createdAfter,
                'created_before': createdBefore,
            },
            errors: {
                404: `Not found`,
                422: `Validation Error`,
            },
        });
    }

}
