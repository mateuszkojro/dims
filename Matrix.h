//
// Created by mateusz on 06.02.2021.
//

#ifndef AVI_PARSER_MATRIX_H
#define AVI_PARSER_MATRIX_H

#include <vector>

template<class T>
class Matrix {
public:
    T& operator()(size_t x , size_t y);

private:
    size_t size_x_;
    size_t size_y_;
    std::vector<T> data_;
};

template<class T>
T &Matrix<T>::operator()(size_t x, size_t y) {
    return data_.at(x + size_x_ * y);
}


#endif //AVI_PARSER_MATRIX_H
