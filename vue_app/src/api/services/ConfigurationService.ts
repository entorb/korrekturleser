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
     * Returns:
     * ConfigResponse: Current LLM provider and available models
     * @returns ConfigResponse Successful Response
     * @throws ApiError
     */
    public static getConfigApiConfigGet(): CancelablePromise<ConfigResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/config/',
        });
    }
}
