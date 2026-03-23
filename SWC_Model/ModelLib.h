/*******************************************************************************
 * @file    ModelLib.h
 * @brief   Auto-generated Inference Engine Header
 * @author  Fran Martin Aguilar
 * @date    2026-03-22
 *
 * --- ESTIMATED RESOURCE FOOTPRINT ---
 * ROM (Flash):    ~44.34 KB
 * RAM (Stack):    ~4224 Bytes
 *******************************************************************************/
#ifndef ModelLib_Engine_H
#define ModelLib_Engine_H

/* Contract: The model expects an array of 384 doubles */
extern void model_predict(double * input, double * output);

#endif /* ModelLib_Engine_H */
