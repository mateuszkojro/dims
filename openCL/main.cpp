#include <iostream>
#include "OpenclProgram.h"

void matrix_add() {
    OpenclProgram GPU("../matrix_add.cl");

    const int size = 2;

    float matrix1[size] = {10.0, 1.0};
    float matrix2[size] = {10.0, 1.0};
    float out[size] = {0, 0};


    auto matrix1_id_id = GPU.add_rw_mem_buffer(size * sizeof(float), matrix1);
    auto matrix2_id_id = GPU.add_rw_mem_buffer(size * sizeof(float), matrix2);
    auto out_id = GPU.add_r_mem_buffer(size * sizeof(float));
    auto size_id = GPU.add_rw_mem_buffer(sizeof(int), (void *) &size);
    GPU.run_task();
    GPU.read_mem_buff(out_id, out);

    for (int i = 0; i < size; i++) {
        std::cout << i << ": " << out[i] << std::endl;
    }
}

void matrix_multiply() {
    OpenclProgram program("../matrix_multiply.cl");

    const int size1_x = 2;
    const int size1_y = 2;
    float matrix1[size1_x * size1_y] = {1.0, 2.0, 3.0, 4.0};


    const int size2_x = 2;
    const int size2_y = 2;
    float matrix2[size2_x * size2_y] = {1.0, 2.0, 3.0, 4.0};

    program.add_rw_mem_buffer(size1_x * size1_y * sizeof(float), matrix1);
    program.add_rw_mem_buffer(sizeof(int),(void*) size1_x);
    program.add_rw_mem_buffer(sizeof(int),(void*) size1_y);


    program.add_rw_mem_buffer(size2_x * size2_y * sizeof(float), matrix2);
    program.add_rw_mem_buffer(sizeof(int),(void*) size2_x);
    program.add_rw_mem_buffer(sizeof(int),(void*) size2_y);


    float out[size1_x * size2_y] = {0, 0, 0, 0};
    program.add_r_mem_buffer(size1_x * size2_y * sizeof(float));
}

int main() {

    matrix_add();

    return 0;
}
