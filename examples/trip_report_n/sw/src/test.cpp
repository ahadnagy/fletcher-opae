// Copyright 2021 Teratide B.V.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <iostream>

#include "./log.h"
#include "./opae_allocator.h"
#include "./opae_trip_report_impl.h"

const int num_parsers = 8;
const int num_jsons = 2;

int main(int argc, char **argv) {
  OpaeAllocator alloc;

  std::vector<RawJSONBuffer> buffers(num_parsers);
  std::vector<RawJSONBuffer *> buffers_ptr(num_parsers);
  std::vector<ParsedBuffer> outputs(num_parsers);

  // Create buffer wrappers, allocate buffers, copy test string into buffers.

  for (int i = 0; i < num_parsers; i++) {
    std::string test_string = R"( {
    "timestamp": "2005-09-09T11:59:06-10:01",
    "accel_decel": 11446688,
    "timezone": 883,
    "vin": 8834555,
    "odometer": 99711112,
    "hypermiling": false,
    "avgspeed": 156,
    "sec_in_band": [3403, 893, 2225, 78, 162, 2332, 1473, 2587, 3446, 178, 997, 2403],
    "miles_in_time_range": [3376, 2553, 2146, 919, 2241, 1044, 1079, 3751, 1665, 2062, 46, 2868, 375, 3305, 4109, 3319, 627, 3523, 2225, 357, 1653, 2757, 3477, 3549],
    "const_speed_miles_in_band": [4175, 2541, 2841, 157, 2922, 651, 315, 2484, 2696, 165, 1366, 958],
    "vary_speed_miles_in_band": [2502, 155, 1516, 1208, 2229, 1850, 4032, 3225, 2704, 2064, 484, 3073],
    "sec_decel": [722, 2549, 547, 3468, 844, 3064, 2710, 1515, 763, 2972],
    "sec_accel": [4175, 2541, 2841, 157, 2922, 651, 315, 2484, 2696, 165, 1366, 958],
    "accel": [1780, 228, 1267, 2389, 437, 871],
    "orientation": false,
    "braking": [724, 2549, 547],
    "small_speed_var": [724, 2549, 54788],
    "large_speed_var": [724, 2549, 5478],
    "speed_changes": 156
}\n)";


    size_t num_bytes = test_string.length();
    std::cout << "JSON " << i << ", len: " << num_bytes << " = " << test_string;
    alloc.Allocate(opae_fixed_capacity, &buffers[i].data_);
    std::memcpy(buffers[i].data_, test_string.data(), num_bytes);
    buffers[i].size_ = num_bytes;
    buffers[i].capacity_ = opae_fixed_capacity;
    buffers_ptr[i] = &buffers[i];
  }

  // Set up manager.
  std::shared_ptr<OpaeTripReportParserManager> m;
  OpaeTripReportParserManager::Make(OpaeBatteryOptions{},
                                 buffers_ptr,
                                 num_parsers,
                                 &m);

  // Parse buffer with every parser.
  auto parsers = m->parsers();
  for (int i = 0; i < num_parsers; i++) {
    parsers[i]->SetInput(&buffers[i], i);
    std::cout << outputs[i].batch->ToString() << std::endl;
  }

  return 0;
}
