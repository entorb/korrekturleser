/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Text improvement response schema.
 */
export type ImproveResponse = {
    text_original: string;
    text_ai: string;
    mode: ImproveResponse.mode;
    tokens_used: number;
    model: string;
    provider: string;
};
export namespace ImproveResponse {
    export enum mode {
        CORRECT = 'correct',
        IMPROVE = 'improve',
        SUMMARIZE = 'summarize',
        EXPAND = 'expand',
        TRANSLATE_DE = 'translate_de',
        TRANSLATE_EN = 'translate_en',
    }
}

