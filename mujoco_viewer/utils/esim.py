#
#BSD 3-Clause License
#
#
#
#Copyright 2022 fortiss, Neuromorphic Computing group
#
#
#All rights reserved.
#
#
#
#Redistribution and use in source and binary forms, with or without
#
#modification, are permitted provided that the following conditions are met:
#
#
#
#* Redistributions of source code must retain the above copyright notice, this
#
#  list of conditions and the following disclaimer.
#
#
#
#* Redistributions in binary form must reproduce the above copyright notice,
#
#  this list of conditions and the following disclaimer in the documentation
#
#  and/or other materials provided with the distribution.
#
#
#
#* Neither the name of the copyright holder nor the names of its
#
#  contributors may be used to endorse or promote products derived from
#
#  this software without specific prior written permission.
#
#
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#
#AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#
#IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#
#DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#
#FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#
#DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#



import numpy as np
import esim_torch
import torch
import cv2


class Esim_interface:

    def __init__(self, contrast_threshold_negative=0.1, contrast_threshold_positive=0.5, refractory_period_ns=0):
        self._esim = esim_torch.ESIM(contrast_threshold_negative,
                            contrast_threshold_positive,
                            refractory_period_ns)

        self._upsampler = None
        self.first_image = True
        self.image_count = 0

    # from event numpy array to img
    def viz_events(self, events, resolution):

        pos_events = events[events[:,-1]==1]
        neg_events = events[events[:,-1]==-1]

        image_pos = np.zeros(resolution[0]*resolution[1], dtype="uint8")
        image_neg = np.zeros(resolution[0]*resolution[1], dtype="uint8")

        np.add.at(image_pos, (pos_events[:,0]+pos_events[:,1]*resolution[1]).astype("int32"), pos_events[:,-1]**2)
        np.add.at(image_neg, (neg_events[:,0]+neg_events[:,1]*resolution[1]).astype("int32"), neg_events[:,-1]**2)

        image_rgb = np.stack(
            [
                image_pos.reshape(resolution), 
                image_neg.reshape(resolution), 
                np.zeros(resolution, dtype="uint8") 
            ], -1
        ) * 50

        return image_rgb   

    def viz_events2(self, events, resolution):

        pos_events = events[events[:,-1]==1]
        neg_events = events[events[:,-1]==-1]

        image_pos = np.zeros(resolution, dtype="uint8")
        image_neg = np.zeros(resolution, dtype="uint8")

        image_pos[pos_events[:,1],pos_events[:,0]] = 50
        image_neg[neg_events[:,1],neg_events[:,0]] = 50

        image_rgb = np.stack(
            [   image_pos, 
                image_neg, 
                np.zeros(resolution, dtype="uint8")], 
            -1) 

        return image_rgb   

    # from evnent tensor dictionary to a event numpy array
    def t2e(self, tensor_dic):
        if not tensor_dic and not tensor_dic.values():
            raise ValueError

        np_dic = {k: v.numpy() for k, v in tensor_dic.items() }

        return np.stack((np_dic["x"], np_dic["y"], np_dic["t"], np_dic["p"]), axis=1)

    # from event array to img
    def img2e(self, img, t):

        self.image_count += 1

        # if self.image_count < 10:
        #     img = np.ones_like(img) * 255 * (self.image_count % 2)
        #     self.first_image = False
        #     print("@@@@@@@@@@@@@only ones")

        log_image = np.log(img.astype("float32") / 255 + 1e-5)
        log_image = torch.from_numpy(log_image).cuda()

        timestamps = np.array([t])
        timestamps_ns = (timestamps * 1e9).astype("int64")
        timestamps_ns = torch.from_numpy(timestamps_ns).cuda()

        sub_events = self._esim.forward(log_image, timestamps_ns[0])
        
        # for the first image, no events are generated, so this needs to be skipped
        if sub_events is None:
            return None

        sub_events = {k: v.cpu() for k, v in sub_events.items()}    

        # transform to an image
        H, W = img.shape
        e = self.t2e(sub_events)
        im = self.viz_events2(e, [H, W])

        return im, sub_events, e

    