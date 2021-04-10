//
// Created by mateusz on 4/10/21.
//

#ifndef VIDEO_ANALYZER_SIMPLESHOW_H
#define VIDEO_ANALYZER_SIMPLESHOW_H

#include <SDL.h>
#include "Logger.h"

/// Helper class to setup the window show array of pixels then
/// destroy window correctly
class SimpleShow {
public:
    SimpleShow(int width, int height);

    ~SimpleShow();

    /// This sows buffer of grayscale pixels but does it on the same thred so jt takes up a time
    /// but is verry easy to use and implement
    /// \param buff
    /// \param x size in x dimention
    /// \param y size in y dimention
    void imshow(const uint8_t *data, size_t x, size_t y);

private:
    int width_;
    int height_;
    uint32_t *data;
    SDL_Window *window;
    SDL_Renderer *renderer;
};

#endif //VIDEO_ANALYZER_SIMPLESHOW_H
