#include <iostream>
#include <vector>
#include <algorithm>
#include <unordered_map>
#include <cmath>
#include <cstring>

enum COLOR
{
    RED,
    GREEN,
    BLUE,
    ALPHA
};

unsigned char clamp_pixel(float value) {
    if (value < 0.0f) return 0;
    if (value > 255.0f) return 255;
    return (unsigned char)value;
}

float clamp(float value, float min, float max) {
    if (value > max) return max;
    if (value < min) return min;
    return value;
}

float top_down_edge[3][3] = {
    { -1.0f, -1.0f, -1.0f},
    {  0.0f,  0.0f,  0.0f},
    {  1.0f,  1.0f,  1.0f}
};

float left_right_edge[3][3] = {
    { -1.0f, 0.0f, 1.0f},
    { -1.0f, 0.0f, 1.0f},
    { -1.0f, 0.0f, 1.0f}
};

float laplacian[3][3] = {
    {0.0f, 1.0f, 0.0f},
    {1.0f, -4.0f, 1.0f},
    {0.0f, 1.0f, 0.0f}
};

float sobel_x[3][3] = {
    { -1.0f, 0.0f, 1.0f},
    { -2.0f, 0.0f, 2.0f},
    { -1.0f, 0.0f, 1.0f}
};

float sobel_y[3][3] = {
    { -1.0f, -2.0f, -1.0f},
    {  0.0f,  0.0f,  0.0f},
    {  1.0f,  2.0f,  1.0f}
};

unsigned char square(unsigned char value) {
    return clamp_pixel((float)value * (float)value / 255.0f);
}

unsigned char sqroot(unsigned char value) {
    return clamp_pixel(std::sqrt((float)value * 255.0f));
}

unsigned char scale_factor(unsigned char value) {
    #define K 1.1f
    return clamp_pixel((float)value * K);
}

class ImageMatrix {
public:
    unsigned char *data;
    int width, height, channels;

    ImageMatrix(unsigned char *data, int w, int h, int c)
    : data(data), width(w), height(h), channels(c) {}

    unsigned char Get(int row, int col, enum COLOR color) {
        if (row < 0 || row >= height || col < 0 || col >= width) return 0; 
        return data[(row * width + col) * channels + color];
    }

    void Set(int row, int col, enum COLOR color, unsigned char value) {
        if (row >= 0 && row < height && col >= 0 && col < width) {
            data[(row * width + col) * channels + color] = value;
        }
    }

    void Add(ImageMatrix img, float factor = 1) {
        for (int y = 0; y < this->height; ++y) {
            for (int x = 0; x < this->width; ++x) {
                int idx = (y * this->width + x) * this->channels;
                int sumR = this->data[idx] + img.Get(y, x, RED);
                int sumG = this->data[idx + 1] + img.Get(y, x, GREEN);
                int sumB = this->data[idx + 2] + img.Get(y, x, BLUE);
                this->data[idx] = std::min(255, int(factor * float(sumR)));
                this->data[idx + 1] = std::min(255, int(factor * float(sumG)));
                this->data[idx + 2] = std::min(255, int(factor * float(sumB)));
            }
        }
    }

    void Sub(ImageMatrix img, int factor = 1) {
        for (int y = 0; y < this->height; ++y) {
            for (int x = 0; x < this->width; ++x) {
                int idx = (y * this->width + x) * this->channels;
                int sumR = this->data[idx] - img.Get(y, x, RED);
                int sumG = this->data[idx + 1] - img.Get(y, x, GREEN);
                int sumB = this->data[idx + 2] - img.Get(y, x, BLUE);
                this->data[idx] = std::max(0, factor * sumR);
                this->data[idx + 1] = std::max(0, factor * sumG);
                this->data[idx + 2] = std::max(0, factor * sumB);
            }
        }
    }

    void dfdx() {
        size_t size = sizeof(unsigned char) * width * height * channels;
        unsigned char* temp = (unsigned char*)malloc(size);
        memset(temp, 0, size);
        for (int y = 0; y < this->height; ++y) {
            for (int x = 0; x < this->width - 1; ++x) {
                int idx = (y * this->width + x) * this->channels;
                int iidx = (y * this->width + (x+1)) * this->channels;
                temp[idx] = abs(this->data[idx] - this->data[iidx]);
                temp[idx + 1] = abs(this->data[idx + 1] - this->data[iidx + 1]);
                temp[idx + 2] = abs(this->data[idx + 2] - this->data[iidx + 2]);
                if (channels == 4) temp[idx+3] = data[idx+3];
            }
        }
        memcpy(this->data, temp, size);
        ::free(temp);
    }

    void dfdy() {
        size_t size = sizeof(unsigned char) * width * height * channels;
        unsigned char* temp = (unsigned char*)malloc(size);
        memset(temp, 0, size);
        for (int y = 0; y < this->height - 1; ++y) {
            for (int x = 0; x < this->width; ++x) {
                int idx = (y * this->width + x) * this->channels;
                int iidx = ((y+1) * this->width + x) * this->channels;
                temp[idx] = abs(this->data[idx] - this->data[iidx]);
                temp[idx + 1] = abs(this->data[idx + 1] - this->data[iidx + 1]);
                temp[idx + 2] = abs(this->data[idx + 2] - this->data[iidx + 2]);

                if (channels == 4) temp[idx + 3] = data[idx + 3];
            }
        }
        memcpy(this->data, temp, size);
        ::free(temp);
    }

    void dfdx2() {
        size_t size = sizeof(unsigned char) * width * height * channels;
        unsigned char* temp = (unsigned char*)malloc(size);
        memset(temp, 0, size);
        for (int y = 0; y < this->height; ++y) {
            for (int x = 1; x < this->width - 1; ++x) {
                int dx = (y * this->width + (x-1)) * this->channels;
                int idx = (y * this->width + x) * this->channels;
                int iidx = (y * this->width + (x+1)) * this->channels;
                temp[idx] = abs(this->data[dx] + this->data[iidx] - 2*this->data[idx]);
                temp[idx + 1] = abs(this->data[dx + 1] + this->data[iidx + 1] - 2*this->data[idx + 1]);
                temp[idx + 2] = abs(this->data[dx + 2] + this->data[iidx + 2] - 2*this->data[idx + 2]);

                if (channels == 4) temp[idx + 3] = data[idx + 3];
            }
        }
        memcpy(this->data, temp, size);
        ::free(temp);
    }
    
    void dfdy2() {
        size_t size = sizeof(unsigned char) * width * height * channels;
        unsigned char* temp = (unsigned char*)malloc(size);
        memset(temp, 0, size);
        for (int y = 1; y < this->height - 1; ++y) {
            for (int x = 0; x < this->width; ++x) {
                int dx = ((y-1) * this->width + x) * this->channels;
                int idx = (y * this->width + x) * this->channels;
                int iidx = ((y+1) * this->width + x) * this->channels;
                temp[idx] = abs(this->data[dx] + this->data[iidx] - 2*this->data[idx]);
                temp[idx + 1] = abs(this->data[dx + 1] + this->data[iidx + 1] - 2*this->data[idx + 1]);
                temp[idx + 2] = abs(this->data[dx + 2] + this->data[iidx + 2] - 2*this->data[idx + 2]);

                if (channels == 4) temp[idx + 3] = data[idx + 3];
            }
        }
        memcpy(this->data, temp, size);
        ::free(temp);
    }

    void apply_opeartion(unsigned char (*operation)(unsigned char)) {
        for (int y = 0; y < this->height; ++y) {
            for (int x = 0; x < this->width; ++x) {
                int idx = (y * this->width + x) * this->channels;
                this->data[idx] = operation(this->data[idx]);
                this->data[idx + 1] = operation(this->data[idx + 1]);
                this->data[idx + 2] = operation(this->data[idx + 2]);
            }
        }
    }

    ImageMatrix* copy() {
        unsigned char* new_data = (unsigned char*)malloc(sizeof(unsigned char) * width * height * channels);
        memcpy(new_data, this->data, sizeof(unsigned char) * width * height * channels);
        return new ImageMatrix(new_data, width, height, channels);
    }


    void free() {
        if (data) {
            ::free(data);
            data = nullptr;
        }
    }
};

extern "C" {
    #define EXPORT __declspec(dllexport)

    EXPORT void gray_scale(unsigned char *data, int width, int height, int channel){
        for (int y = 0; y < height; ++y)
        {
            for (int x = 0; x < width; ++x)
            {
                int idx = (y * width + x) * channel;
                unsigned char gray_value = (data[idx] + data[idx + 1] + data[idx + 2]) / 3;
                data[idx] = data[idx + 1] = data[idx + 2] = gray_value;
            }
        }
    }

    EXPORT void blured(unsigned char *data, int width, int height, int channel, int radius){
        unsigned char *temp = (unsigned char *)malloc(sizeof(unsigned char) * width * height * channel);
        // memcpy(new_image, data, width * height * channel);

        int kernel_radius = radius;
        int kernel_size = kernel_radius * 2 + 1;

        for (int y = 0; y < height; ++y) {
            float sumR = 0, sumG = 0, sumB = 0;
            for (int r = -kernel_radius; r <= kernel_radius; ++r) {
                int x = clamp(r, 0, width-1);
                int idx = (y * width + x) * channel;
                sumR += data[idx];
                sumG += data[idx+1];
                sumB += data[idx+2];
            }

            for (int x = 0; x < width; ++x) {
                int idx = (y * width + x) * channel;
                temp[idx] = (sumR/float(kernel_size));
                temp[idx + 1] = (sumG/float(kernel_size));
                temp[idx + 2] = (sumB/float(kernel_size));

                if (channel == 4) temp[idx + 3] = data[idx + 3];
                int left  = clamp(x - kernel_radius, 0, width - 1);
                int right = clamp(x + kernel_radius + 1, 0, width - 1);
                
                int l_idx = (y * width + left) * channel;
                int r_idx = (y * width + right) * channel;

                sumR += (float)data[r_idx] - (float)data[l_idx];
                sumG += (float)data[r_idx + 1] - (float)data[l_idx + 1];
                sumB += (float)data[r_idx + 2] - (float)data[l_idx + 2];
            }
        }


        for (int x = 0; x < width; ++x) {
            float sumR = 0, sumG = 0, sumB = 0;
            for (int c = -kernel_radius; c <= kernel_radius; ++c) {
                int y = clamp(c, 0, height - 1);
                int idx = (y * width + x) * channel;
                sumR += temp[idx];
                sumG += temp[idx + 1];
                sumB += temp[idx + 2];
            }

            for (int y = 0; y < height; ++y) {
                int idx = (y * width + x) * channel;
                data[idx]     = (unsigned char)(sumR / kernel_size);
                data[idx + 1] = (unsigned char)(sumG / kernel_size);
                data[idx + 2] = (unsigned char)(sumB / kernel_size);

                int top    = clamp(y - kernel_radius, 0, height - 1);
                int bottom = clamp(y + kernel_radius + 1, 0, height - 1);

                int t_idx = (top * width + x) * channel;
                int b_idx = (bottom * width + x) * channel;

                sumR += (float)temp[b_idx] - (float)temp[t_idx];
                sumG += (float)temp[b_idx + 1] - (float)temp[t_idx + 1];
                sumB += (float)temp[b_idx + 2] - (float)temp[t_idx + 2];
            }
        }
        free(temp);
    }

    EXPORT void add_images(unsigned char* dest_data, unsigned char * source_data, int width, int height, int channel) {
        if (dest_data == nullptr || source_data == nullptr) return;

        ImageMatrix destination(dest_data, width, height, channel);
        ImageMatrix source(source_data, width, height, channel);

        destination.Add(source);
    }

    EXPORT void sub_images(unsigned char* dest_data, unsigned char * source_data, int width, int height, int channel) {
        if (dest_data == nullptr || source_data == nullptr) return;

        ImageMatrix destination(dest_data, width, height, channel);
        ImageMatrix source(source_data, width, height, channel);

        destination.Sub(source);
    }

    EXPORT void inverted(unsigned char *data, int width, int height, int channel){
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x)
            {
                int idx = (y * width + x) * channel;
                data[idx] = 255 - data[idx];
                data[idx + 1] = 255 - data[idx + 1];
                data[idx + 2] = 255 - data[idx + 2];
            }
        }
    }

    EXPORT void threshold(unsigned char *data, int width, int height, int channel, unsigned char threshold_value){
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                int idx = (y * width + x) * channel;
                data[idx] = (data[idx] > threshold_value) ? data[idx] : 0;
                data[idx + 1] = (data[idx + 1] > threshold_value) ? data[idx + 1] : 0;
                data[idx + 2] = (data[idx + 2] > threshold_value) ? data[idx + 2] : 0;
            }
        }
    }

    EXPORT void log_transform(unsigned char *data, int width, int height, int channel, int c){
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                int idx = (y * width + x) * channel;
                data[idx] = std::min(255, static_cast<int>(c * std::log(1 + data[idx])));
                data[idx+1] = std::min(255, static_cast<int>(c * std::log(1 + data[idx+1])));
                data[idx+2] = std::min(255, static_cast<int>(c * std::log(1 + data[idx+2])));
            }
        }
    }

    EXPORT void power_transform(unsigned char *data, int width, int height, int channel, int c, double gamma){
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                int idx = (y * width + x) * channel;
                data[idx] = std::min(255, static_cast<int>(c * std::pow(data[idx], gamma)));
                data[idx+1] = std::min(255, static_cast<int>(c * std::pow(data[idx+1], gamma)));
                data[idx+2] = std::min(255, static_cast<int>(c * std::pow(data[idx+2], gamma)));
            }
        }
    }

    EXPORT void max_filter(unsigned char *data, int width, int height, int channel, int radius) {
        if (channel < 3) return;
        size_t size = (size_t)width * height * channel;
        std::vector<unsigned char> new_image(size);
        
        memcpy(new_image.data(), data, size); 

        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                unsigned char maxR = 0, maxG = 0, maxB = 0;

                for (int ir = -radius; ir <= radius; ++ir) {
                    for (int ic = -radius; ic <= radius; ++ic) {
                        int iy = clamp(y + ir, 0, height - 1);
                        int ix = clamp(x + ic, 0, width - 1);
                        int idx = (iy * width + ix) * channel;

                        maxR = std::max(maxR, data[idx]);
                        maxG = std::max(maxG, data[idx + 1]);
                        maxB = std::max(maxB, data[idx + 2]);
                    }
                }

                int out_idx = (y * width + x) * channel;
                new_image[out_idx] = maxR;
                new_image[out_idx + 1] = maxG;
                new_image[out_idx + 2] = maxB;
            }
        }
        memcpy(data, new_image.data(), size);
    }

    EXPORT void min_filter(unsigned char *data, int width, int height, int channel, int radius) {
        if (channel < 3) return;
        size_t size = (size_t)width * height * channel;
        std::vector<unsigned char> new_image(size);
        memcpy(new_image.data(), data, size);

        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                unsigned char minR = 255, minG = 255, minB = 255;

                for (int ir = -radius; ir <= radius; ++ir) {
                    for (int ic = -radius; ic <= radius; ++ic) {
                        int iy = clamp(y + ir, 0, height - 1);
                        int ix = clamp(x + ic, 0, width - 1);
                        int idx = (iy * width + ix) * channel;

                        minR = std::min(minR, data[idx]);
                        minG = std::min(minG, data[idx + 1]);
                        minB = std::min(minB, data[idx + 2]);
                    }
                }

                int out_idx = (y * width + x) * channel;
                new_image[out_idx] = minR;
                new_image[out_idx + 1] = minG;
                new_image[out_idx + 2] = minB;
            }
        }
        memcpy(data, new_image.data(), size);
    }

    EXPORT void median_filter(unsigned char* data, int width, int height, int channel, int radius) {
        if (channel < 3) return;
        size_t size = (size_t)width * height * channel;
        std::vector<unsigned char> new_image(size);
        memcpy(new_image.data(), data, size);

        int kernel_size = radius * 2 + 1;
        int pixel_count = kernel_size * kernel_size;
        int median_pixel = pixel_count / 2;

        std::vector<unsigned char> windowR(pixel_count);
        std::vector<unsigned char> windowG(pixel_count);
        std::vector<unsigned char> windowB(pixel_count);

        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                int count = 0;

                for (int ir = -radius; ir <= radius; ++ir) {
                    for (int ic = -radius; ic <= radius; ++ic) {
                        int iy = clamp(y + ir, 0, height - 1);
                        int ix = clamp(x + ic, 0, width - 1);
                        int idx = (iy * width + ix) * channel;

                        windowR[count] = data[idx];
                        windowG[count] = data[idx + 1];
                        windowB[count] = data[idx + 2];
                        count++;
                    }
                }

                std::nth_element(windowR.begin(), windowR.begin() + median_pixel, windowR.end());
                std::nth_element(windowG.begin(), windowG.begin() + median_pixel, windowG.end());
                std::nth_element(windowB.begin(), windowB.begin() + median_pixel, windowB.end());

                int out_idx = (y * width + x) * channel;
                new_image[out_idx] = windowR[median_pixel];
                new_image[out_idx + 1] = windowG[median_pixel];
                new_image[out_idx + 2] = windowB[median_pixel];
            }
        }
        memcpy(data, new_image.data(), size);
    }

    EXPORT void mode_filter(unsigned char* data, int width, int height, int channel, int radius) {
        if (channel < 3) return;
        size_t size = (size_t)width * height * channel;
        std::vector<unsigned char> new_image(size);
        memcpy(new_image.data(), data, size);

        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                int countR[256] = {0}, countG[256] = {0}, countB[256] = {0};

                for (int ir = -radius; ir <= radius; ++ir) {
                    for (int ic = -radius; ic <= radius; ++ic) {
                        int iy = clamp(y + ir, 0, height - 1);
                        int ix = clamp(x + ic, 0, width - 1);
                        int idx = (iy * width + ix) * channel;

                        countR[data[idx]]++;
                        countG[data[idx + 1]]++;
                        countB[data[idx + 2]]++;
                    }
                }

                unsigned char modeR = 0, modeG = 0, modeB = 0;
                int maxR = 0, maxG = 0, maxB = 0;

                for (int i = 0; i < 256; ++i) {
                    if (countR[i] > maxR) { maxR = countR[i]; modeR = (unsigned char)i; }
                    if (countG[i] > maxG) { maxG = countG[i]; modeG = (unsigned char)i; }
                    if (countB[i] > maxB) { maxB = countB[i]; modeB = (unsigned char)i; }
                }

                int out_idx = (y * width + x) * channel;
                new_image[out_idx] = modeR;
                new_image[out_idx + 1] = modeG;
                new_image[out_idx + 2] = modeB;
            }
        }
        memcpy(data, new_image.data(), size);
    }

    EXPORT void first_derivative_x(unsigned char* data, int width, int height, int channel) {
        ImageMatrix img(data, width, height, channel);
        img.dfdx();
    }

    EXPORT void first_derivative_y(unsigned char* data, int width, int height, int channel) {
        ImageMatrix img(data, width, height, channel);
        img.dfdy();
    }

    EXPORT void second_derivative_x(unsigned char* data, int width, int height, int channel) {
        ImageMatrix img(data, width, height, channel);
        img.dfdx2();
    }
    
    EXPORT void second_derivative_y(unsigned char* data, int width, int height, int channel) {
        ImageMatrix img(data, width, height, channel);
        img.dfdy2();
    }

    EXPORT void multiply(unsigned char* data, int width, int height, int channel, float factor) {
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                int idx = (y * width + x) * channel;
                data[idx] = clamp_pixel(factor * float(data[idx]));
                data[idx+1] = clamp_pixel(factor * float(data[idx+1]));
                data[idx+2] = clamp_pixel(factor * float(data[idx+2]));
            }
        }
    }
}