#import <Capacitor/Capacitor.h>

CAP_PLUGIN(SaveToGalleryPlugin, "SaveToGallery",
           CAP_PLUGIN_METHOD(saveVideo, CAPPluginReturnPromise);
)

