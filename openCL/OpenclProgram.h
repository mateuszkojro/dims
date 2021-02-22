/*
 * Wraper class around OpenCL calls to make using it feasible in larger proj.
 */

#ifndef OPENCL_OPENCLPROGRAM_H
#define OPENCL_OPENCLPROGRAM_H

#ifdef __APPLE__
#include <OpenCL/opencl.h>
#else

#include <CL/cl.h>

#endif

#include <string>
#include <assert.h>
#include <vector>

struct OpenclSource {
    char *buffer_;
    size_t size_;
};

struct OpenclBuffer {
    cl_mem buffer_;
    size_t size_;
};

#define MAX_SOURCE_SIZE (0x100000)

static OpenclSource load_source(std::string path) {

    FILE *fp;
    char *source_str;
    size_t source_size;

    /* Load the source code containing the kernel*/
    fp = fopen(path.c_str(), "r");
    if (!fp) {
        fprintf(stderr, "Failed to load kernel source.\n");
        exit(1);
    }

    source_str = (char *) malloc(MAX_SOURCE_SIZE);
    source_size = fread(source_str, 1, MAX_SOURCE_SIZE, fp);

    return {
            .buffer_ = source_str,
            .size_ = source_size
    };
}

class OpenclProgram {
public:
    OpenclProgram(std::string path);

    ~OpenclProgram();

    size_t add_r_mem_buffer(size_t size);

    size_t add_rw_mem_buffer(size_t size, void *ptr);

    void read_mem_buff(size_t idx, void *ptr);

    void run_task();

private:
    void set_device_id(int device_index);

    void create_context();

    void create_command_queue();

    void create_kernel(OpenclSource source);

private:
    cl_context context_;
    cl_command_queue command_queue_;
    cl_kernel kernel_;
    cl_device_id device_id_;

    std::vector<OpenclBuffer> buffers_;

};
#endif //OPENCL_OPENCLPROGRAM_H
