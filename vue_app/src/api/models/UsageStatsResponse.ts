/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DailyUsage } from './DailyUsage';
import type { TotalUsage } from './TotalUsage';
/**
 * Usage statistics response.
 */
export type UsageStatsResponse = {
    daily: Array<DailyUsage>;
    total: Array<TotalUsage>;
};

