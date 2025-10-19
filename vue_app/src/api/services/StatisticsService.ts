/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UsageStatsResponse } from '../models/UsageStatsResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class StatisticsService {
    /**
     * Get All Stats
     * Get usage statistics (daily and total).
     *
     * - Admin (user_id=1): Returns stats for all users
     * - Non-admin: Returns stats only for the current user (single row)
     * - PROD: Queries database and returns data with all values set to 0
     * - Local: Returns mock data with all values set to 0
     *
     * Args:
     * current_user: Authenticated user (injected by dependency)
     *
     * Returns:
     * UsageStatsResponse: Daily and total usage statistics
     * @returns UsageStatsResponse Successful Response
     * @throws ApiError
     */
    public static getAllStatsApiStatsGet(): CancelablePromise<UsageStatsResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/stats/',
        });
    }
}
