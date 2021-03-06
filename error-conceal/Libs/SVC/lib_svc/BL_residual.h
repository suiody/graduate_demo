/*****************************************************************************
   *
   *  Open SVC Decoder developped in IETR image lab
   *
   *
   *
   *              M�d�ric BLESTEL <mblestel@insa-rennes.Fr>
   *              Mickael RAULET <mraulet@insa-rennes.Fr>
   *              http://www.ietr.org/
   *
   *
   *
   *
   *
   * This library is free software; you can redistribute it and/or
   * modify it under the terms of the GNU Lesser General Public
   * License as published by the Free Software Foundation; either
   * version 2 of the License, or (at your option) any later version.
   *
   * This library is distributed in the hope that it will be useful,
   * but WITHOUT ANY WARRANTY; without even the implied warranty of
   * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
   * Lesser General Public License for more details.
   *
   * You should have received a copy of the GNU Lesser General Public
   * License along with this library; if not, write to the Free Software
   * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
   *
   *
   * $Id$
   *
   **************************************************************************/


#ifndef BL_RES_H
#define BL_RES_H

void decode_Intra4x4_BL_lum ( unsigned char * image, RESIDU *CurrResidu,const  short PicWidthInPix, const short W4x4_intra [6][16]);
void decode_Intra8x8_BL_lum ( unsigned char * image, RESIDU *CurrResidu,const  short PicWidthInPix, const short W8x8_intra [6][64] );
void DecodeChromaBL (unsigned char image_Cb [], unsigned char image_Cr [], const PPS *pps, RESIDU *residu, const short PicWidthInPix, const W_TABLES *quantif);
void ComputeCurrentResidual(const NAL *Nal, RESIDU *CurrResidu, RESIDU *BaseResidu, const PPS *pps, const W_TABLES *Quantif, const short PicWidthInPix
							, unsigned char *Y, unsigned char *U, unsigned char *V);
#endif
