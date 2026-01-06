/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ConfigResponse } from '../models/ConfigResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ConfigurationService {
    /**
     * Get Config
     * Get application configuration.
     *
     * Args:
     * provider: Optional provider to get config for, defaults to default provider
     *
     * Returns:
     * ConfigResponse: Current LLM provider, available models, and all providers
     * @param provider
     * @returns ConfigResponse Successful Response
     * @throws ApiError
     */
    public static getConfigApiConfigGet(
        provider?: (string | null),
    ): CancelablePromise<ConfigResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/config/',
            query: {
                'provider': provider,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
