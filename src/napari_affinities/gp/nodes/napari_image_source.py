from napari.layers import Image

import gunpowder as gp
from gunpowder.profiling import Timing
from gunpowder.array_spec import ArraySpec

import numpy as np


class NapariImageSource(gp.BatchProvider):
    """
    A gunpowder interface to a napari Image
    Args:
        image (Image):
            The napari Image to pull data from
        key (``gp.ArrayKey``):
            The key to provide data into
    """

    def __init__(self, image: Image, key: gp.ArrayKey):
        self.array_spec = self._read_metadata(image)
        self.image = gp.Array(self._remove_leading_dims(image.data), self.array_spec)
        self.key = key

    def setup(self):
        self.provides(self.key, self.array_spec.copy())

    def provide(self, request):
        output = gp.Batch()

        timing_provide = Timing(self, "provide")
        timing_provide.start()

        output[self.key] = self.image.crop(request[self.key].roi)

        timing_provide.stop()

        output.profiling_stats.add(timing_provide)

        return output

    def _remove_leading_dims(self, data):
        print(data.shape)
        while data.shape[0] == 1:
            data = data[0]
            print(data.shape)
        return data

    def _read_metadata(self, image):
        # offset assumed to be in world coordinates
        # TODO: read from metadata
        offset = gp.Coordinate(image.metadata.get("offset", (1, 1)))
        voxel_size = gp.Coordinate(image.metadata.get("resolution", (1, 1)))
        shape = gp.Coordinate(image.data.shape[-offset.dims() :])

        return gp.ArraySpec(
            roi=gp.Roi(offset, voxel_size * shape),
            dtype=image.dtype,
            interpolatable=True,
            voxel_size=voxel_size,
        )
