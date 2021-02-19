//
// Created by mateusz on 17.02.2021.
//

#include "OpenclProgram.h"

OpenclProgram::OpenclProgram(std::string path) {
    set_device_id(0);
    create_context();
    create_command_queue();

    auto source = load_source(path);
    create_kernel(source);

}


void OpenclProgram::set_device_id(int index) {
    cl_device_id device_id = NULL;
    cl_platform_id platform_id = NULL;
    cl_uint ret_num_devices;
    cl_uint ret_num_platforms;
    cl_int err = 0;

    err = clGetPlatformIDs(1, &platform_id, &ret_num_platforms);
    assert(!err);

    err = clGetDeviceIDs(platform_id, CL_DEVICE_TYPE_DEFAULT, 1, &device_id, &ret_num_devices);
    assert(!err);

    device_id_ = device_id;
}

void OpenclProgram::create_context() {
    cl_context context;
    cl_int err = 0;
    /* Create OpenCL context */
    context = clCreateContext(NULL, 1, &device_id_, NULL, NULL, &err);
    printf("context: %s\n", context);
    assert(!err);
    context_ = context;
}

void OpenclProgram::create_command_queue() {
    cl_command_queue command_queue = NULL;
    cl_int err = 0;
    /* Create Command Queue */
    command_queue = clCreateCommandQueue(context_, device_id_, 0, &err);

    assert(!err);
    command_queue_ = command_queue;
}

void OpenclProgram::create_kernel(OpenclSource source) {
    cl_int err = 0; // error handling value

    /* Create Kernel Program from the source */
    cl_program program = clCreateProgramWithSource(
            context_,
            1,
            (const char **) &source.buffer_,
            (const size_t *) &source.size_, &err
    );
    assert(!err);

    /* Build Kernel Program */
    err = clBuildProgram(program, 1, &device_id_, NULL, NULL, NULL);

    assert(!err);
    /* Create OpenCL Kernel */
    // TODO: name should be changin or there might be problems i guess
    cl_kernel kernel = clCreateKernel(program, "hello", &err);

    assert(!err);
    kernel_ = kernel;

}

size_t OpenclProgram::add_r_mem_buffer(size_t size) {
    cl_int err = 0;

    size_t id = buffers_.size();

    /* Create Memory Buffers */
    cl_mem memobj = clCreateBuffer(context_, CL_MEM_READ_WRITE, size, NULL, &err);
    assert(!err);

    OpenclBuffer buffer = {.buffer_ = memobj, .size_ = size};

    err = clSetKernelArg(kernel_, id, sizeof(cl_mem), (void *) &memobj);

    buffers_.push_back(buffer);

    return id;
}

OpenclProgram::~OpenclProgram() {
    cl_int err = 0;
    /* Finalization */
    err = clFlush(command_queue_);
    err = clReleaseKernel(kernel_);

    //TODO: i am never releasing the program
    //err = clReleaseProgram(program_);

    for (auto &buffer : buffers_) {
        clReleaseMemObject(buffer.buffer_);
    }

    err = clReleaseCommandQueue(command_queue_);
    err = clReleaseContext(context_);

    assert(!err);
}

size_t OpenclProgram::add_rw_mem_buffer(size_t size, void *ptr) {
    cl_int err = 0;

    size_t id = buffers_.size();

    /* Create Memory Buffers */
    cl_mem memobj = clCreateBuffer(context_, CL_MEM_READ_WRITE, size, NULL, &err);
    assert(!err);

    OpenclBuffer buffer = {.buffer_ = memobj, .size_ = size};

    err = clSetKernelArg(kernel_, id, sizeof(cl_mem), (void *) &memobj);

    err = clEnqueueWriteBuffer(command_queue_, memobj, CL_TRUE, 0, size, (void *) ptr, 0, NULL, NULL);

    buffers_.push_back(buffer);

    return id;
}

void OpenclProgram::read_mem_buff(size_t idx, void *ptr) {
    cl_int err = 0;
    err = clEnqueueReadBuffer(command_queue_, buffers_[idx].buffer_, CL_TRUE, 0,
                              buffers_[idx].size_, ptr, 0, NULL, NULL);

    assert(!err);
}

void OpenclProgram::run_task() {
    cl_int err = 0;
    /* Execute OpenCL Kernel */
    err = clEnqueueTask(command_queue_, kernel_, 0, NULL, NULL);
}

