/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TextRequest } from '../models/TextRequest';
import type { TextResponse } from '../models/TextResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class TextImprovementService {
    /**
     * Improve Text
     * Improve text using AI based on the selected mode.
     * @param requestBody
     * @returns TextResponse Successful Response
     * @throws ApiError
     */
    public static improveTextApiTextPost(
        requestBody: TextRequest,
    ): CancelablePromise<TextResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/text/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
