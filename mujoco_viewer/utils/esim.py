
import numpy as np
import esim_torch
import torch
import cv2

class Esim_interface:

    def __init__(self, contrast_threshold_negative=0.1, contrast_threshold_positive=0.5, refractory_period_ns=0):
        self._esim = esim_torch.ESIM(contrast_threshold_negative,
                            contrast_threshold_positive,
                            refractory_period_ns)

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

    # from evnent tensor dictionary to a event numpy array
    def t2e(self, tensor_dic):
        if not tensor_dic and not tensor_dic.values():
            raise ValueError

        np_dic = {k: v.numpy() for k, v in tensor_dic.items() }

        size = list(np_dic.values())[0].size

        lis = []
        for i in range(size):
            event = []
            for v in np_dic.values():
                event.append(v[i])
            lis.append(event)

        return np.array(lis) 

    # from event array to img
    def img2e(self, img, t):
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
        im = self.viz_events(e, [H, W])

        return im, sub_events