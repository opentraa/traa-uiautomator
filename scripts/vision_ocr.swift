import Foundation
import Vision
import CoreGraphics
import ImageIO

struct OcrMatch: Encodable {
    struct OcrRect: Encodable {
        let x: Int
        let y: Int
        let width: Int
        let height: Int
    }

    let text: String
    let confidence: Double
    let rect: OcrRect
}

enum VisionOcrError: Error {
    case invalidArguments
    case loadImageFailed
}

func loadImage(url: URL) throws -> CGImage {
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil),
          let image = CGImageSourceCreateImageAtIndex(source, 0, nil) else {
        throw VisionOcrError.loadImageFailed
    }
    return image
}

func main() throws {
    guard CommandLine.arguments.count >= 3 else {
        throw VisionOcrError.invalidArguments
    }

    let imagePath = CommandLine.arguments[1]
    let query = CommandLine.arguments[2].lowercased()
    let imageURL = URL(fileURLWithPath: imagePath)
    let image = try loadImage(url: imageURL)

    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = true

    let handler = VNImageRequestHandler(cgImage: image, options: [:])
    try handler.perform([request])

    let width = image.width
    let height = image.height

    guard let observations = request.results else {
        return
    }

    let encoder = JSONEncoder()
    for observation in observations {
        guard let candidate = observation.topCandidates(1).first else { continue }
        if !candidate.string.lowercased().contains(query) {
            continue
        }

        let box = observation.boundingBox
        let rect = OcrMatch.OcrRect(
            x: Int(box.origin.x * CGFloat(width)),
            y: Int((1.0 - box.origin.y - box.size.height) * CGFloat(height)),
            width: Int(box.size.width * CGFloat(width)),
            height: Int(box.size.height * CGFloat(height))
        )

        let match = OcrMatch(
            text: candidate.string,
            confidence: Double(candidate.confidence),
            rect: rect
        )
        let data = try encoder.encode(match)
        if let line = String(data: data, encoding: .utf8) {
            print(line)
        }
    }
}

do {
    try main()
} catch {
    fputs("vision_ocr error: \\(error)\\n", stderr)
    exit(1)
}
