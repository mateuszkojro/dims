//
// Created by mateusz on 4/10/21.
//

#include <cassert>
#include "SImpleShow.h"

/// Setup the window with the width and height
/// \param width width of the window
/// \param height height of thw window
SimpleShow::SimpleShow(int width, int height) :
        width_(width),
        height_(height) {

    // retutns zero on success else non-zero
    if (SDL_Init(SDL_INIT_EVERYTHING) != 0) {
        printf("error initializing SDL: %s\n", SDL_GetError());
    }

    // create a window
    this->window = SDL_CreateWindow("Video Player",
                                    0,
                                    0,
                                    this->width_,
                                    this->height_,
                                    0);

    // triggers the program that controls
    // your graphics hardware and sets flags
    Uint32 render_flags = SDL_RENDERER_ACCELERATED;

    // creates a renderer to render our images
    this->renderer = SDL_CreateRenderer(this->window, -1, render_flags);

    // allocate buffer for storing frames
    this->data = new uint32_t[width_ * height_];
}

/// Destruct all the allocated memory
SimpleShow::~SimpleShow() {

    // deallocate data buffer
    delete[] this->data;

    // destroy renderer
    SDL_DestroyRenderer(this->renderer);

    // destroy window
    SDL_DestroyWindow(this->window);

    // close SDL
    SDL_Quit();
}

void SimpleShow::imshow(const uint8_t *buff, size_t x, size_t y) {


    // convert the grayscale pixels to ARGB8888 format
    for (int i = 0; i < x * y; i++) {
        data[i] = (0xff << 24) | (buff[i] << 16) | (buff[i] << 8) | buff[i];
    }

    // should window be closed
    bool close = false;

    // create the trxture to store data from the pixel array
    SDL_Texture *texture = SDL_CreateTexture(renderer,
                                             SDL_PIXELFORMAT_ARGB8888,
                                             SDL_TEXTUREACCESS_STATIC,
                                             1920,
                                             1080);

    // copy data to the texture
    SDL_UpdateTexture(texture, NULL, data, 1920 * sizeof(Uint32));

    // copy texture to renderer
    SDL_RenderCopy(renderer, texture, NULL, NULL);

    // render
    SDL_RenderPresent(renderer);
}
