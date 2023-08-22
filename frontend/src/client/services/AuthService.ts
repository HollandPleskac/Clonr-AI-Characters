/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_auth_cookie_login_auth_cookies_login_post } from '../models/Body_auth_cookie_login_auth_cookies_login_post';
import type { OAuth2AuthorizeResponse } from '../models/OAuth2AuthorizeResponse';
import type { UserCreate } from '../models/UserCreate';
import type { UserRead } from '../models/UserRead';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class AuthService {

    /**
     * Auth:Cookie.Login
     * @param formData
     * @returns any Successful Response
     * @throws ApiError
     */
    public static authCookieLoginAuthCookiesLoginPost(
        formData: Body_auth_cookie_login_auth_cookies_login_post,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/auth/cookies/login',
            formData: formData,
            mediaType: 'application/x-www-form-urlencoded',
            errors: {
                400: `Bad Request`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Auth:Cookie.Logout
     * @returns any Successful Response
     * @throws ApiError
     */
    public static authCookieLogoutAuthCookiesLogoutPost(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/auth/cookies/logout',
            errors: {
                401: `Missing token or inactive user.`,
            },
        });
    }

    /**
     * Register:Register
     * @param requestBody
     * @returns UserRead Successful Response
     * @throws ApiError
     */
    public static registerRegisterAuthRegisterPost(
        requestBody: UserCreate,
    ): CancelablePromise<UserRead> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/auth/register',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Bad Request`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Oauth:Google.Cookie.Authorize
     * @param scopes
     * @returns OAuth2AuthorizeResponse Successful Response
     * @throws ApiError
     */
    public static oauthGoogleCookieAuthorizeAuthGoogleAuthorizeGet(
        scopes?: Array<string>,
    ): CancelablePromise<OAuth2AuthorizeResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/auth/google/authorize',
            query: {
                'scopes': scopes,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Oauth:Google.Cookie.Callback
     * The response varies based on the authentication backend used.
     * @param code
     * @param codeVerifier
     * @param state
     * @param error
     * @returns any Successful Response
     * @throws ApiError
     */
    public static oauthGoogleCookieCallbackAuthGoogleCallbackGet(
        code?: (string | null),
        codeVerifier?: (string | null),
        state?: (string | null),
        error?: (string | null),
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/auth/google/callback',
            query: {
                'code': code,
                'code_verifier': codeVerifier,
                'state': state,
                'error': error,
            },
            errors: {
                400: `Bad Request`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Oauth:Facebook.Cookie.Authorize
     * @param scopes
     * @returns OAuth2AuthorizeResponse Successful Response
     * @throws ApiError
     */
    public static oauthFacebookCookieAuthorizeAuthFacebookAuthorizeGet(
        scopes?: Array<string>,
    ): CancelablePromise<OAuth2AuthorizeResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/auth/facebook/authorize',
            query: {
                'scopes': scopes,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Oauth:Facebook.Cookie.Callback
     * The response varies based on the authentication backend used.
     * @param code
     * @param codeVerifier
     * @param state
     * @param error
     * @returns any Successful Response
     * @throws ApiError
     */
    public static oauthFacebookCookieCallbackAuthFacebookCallbackGet(
        code?: (string | null),
        codeVerifier?: (string | null),
        state?: (string | null),
        error?: (string | null),
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/auth/facebook/callback',
            query: {
                'code': code,
                'code_verifier': codeVerifier,
                'state': state,
                'error': error,
            },
            errors: {
                400: `Bad Request`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Oauth:Reddit.Cookie.Authorize
     * @param scopes
     * @returns OAuth2AuthorizeResponse Successful Response
     * @throws ApiError
     */
    public static oauthRedditCookieAuthorizeAuthRedditAuthorizeGet(
        scopes?: Array<string>,
    ): CancelablePromise<OAuth2AuthorizeResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/auth/reddit/authorize',
            query: {
                'scopes': scopes,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Oauth:Reddit.Cookie.Callback
     * The response varies based on the authentication backend used.
     * @param code
     * @param codeVerifier
     * @param state
     * @param error
     * @returns any Successful Response
     * @throws ApiError
     */
    public static oauthRedditCookieCallbackAuthRedditCallbackGet(
        code?: (string | null),
        codeVerifier?: (string | null),
        state?: (string | null),
        error?: (string | null),
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/auth/reddit/callback',
            query: {
                'code': code,
                'code_verifier': codeVerifier,
                'state': state,
                'error': error,
            },
            errors: {
                400: `Bad Request`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Oauth:Discord.Cookie.Authorize
     * @param scopes
     * @returns OAuth2AuthorizeResponse Successful Response
     * @throws ApiError
     */
    public static oauthDiscordCookieAuthorizeAuthDiscordAuthorizeGet(
        scopes?: Array<string>,
    ): CancelablePromise<OAuth2AuthorizeResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/auth/discord/authorize',
            query: {
                'scopes': scopes,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Oauth:Discord.Cookie.Callback
     * The response varies based on the authentication backend used.
     * @param code
     * @param codeVerifier
     * @param state
     * @param error
     * @returns any Successful Response
     * @throws ApiError
     */
    public static oauthDiscordCookieCallbackAuthDiscordCallbackGet(
        code?: (string | null),
        codeVerifier?: (string | null),
        state?: (string | null),
        error?: (string | null),
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/auth/discord/callback',
            query: {
                'code': code,
                'code_verifier': codeVerifier,
                'state': state,
                'error': error,
            },
            errors: {
                400: `Bad Request`,
                422: `Validation Error`,
            },
        });
    }

}
