const std = @import("std");
const zmq = @cImport(@cInclude("zmq.h"));

pub fn main() !void {
    std.log.info("Start", .{});
    var err: c_int = 0;

    const context = zmq.zmq_ctx_new();
    defer _ = zmq.zmq_ctx_term(context);

    std.log.info("zmq_socket - ZMQ_PUB", .{});
    const publisher = zmq.zmq_socket(context, zmq.ZMQ_PUB);

    std.log.info("zmq_socket - ZMQ_SUB", .{});
    const subscriber = zmq.zmq_socket(context, zmq.ZMQ_SUB);

    std.log.info("zmq_bind - publisher", .{});
    err = zmq.zmq_bind(publisher, "tcp://*:5555");
    if (err != 0) {
        return error.zmqError;
    }

    std.log.info("zmq_connect - subscriber", .{});
    err = zmq.zmq_connect(subscriber, "tcp://localhost:5555");
    if (err != 0) {
        return error.zmqError;
    }

    std.log.info("zmq subscirbe", .{});
    err = zmq.zmq_setsockopt(subscriber, zmq.ZMQ_SUBSCRIBE, "", 0);
    if (err != 0) {
        return error.zmqError;
    }

    std.log.info("zmq_send", .{});
    const message = "Hello zmq!";
    err = zmq.zmq_send(publisher, message, message.len, 0);
    if (err != 0) {
        return error.zmqError;
    }

    std.log.info("zmq_recv", .{});
    var recv_message: [message.len]u8 = undefined;
    err = zmq.zmq_recv(subscriber, &recv_message, recv_message.len, 0);
    if (err != 0) {
        return error.zmqError;
    }

    std.log.info("{s}", .{recv_message});
}
