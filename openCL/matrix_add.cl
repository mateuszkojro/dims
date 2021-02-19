float add2(float x) {
    return x + 2;
}

__kernel void hello(__global float *matrix1, __global float *matrix2, __global float *out, __global int *size) {

    out[0] = *size;

    out[1] = *size;

    for (int i = 0; i < *size; i++) {
        out[i] = add2(out[i]); //matrix1[i] + matrix2[i];
    }

}
