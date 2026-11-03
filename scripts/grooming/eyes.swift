import Foundation
import Vision
import AppKit
// Prints eye centers for the largest face in each image. Finds positions only; identifies no one.
for path in CommandLine.arguments.dropFirst() {
  guard let img = NSImage(contentsOfFile: path), let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { print("\(path)\tERR"); continue }
  let W = Double(cg.width), H = Double(cg.height)
  let req = VNDetectFaceLandmarksRequest()
  try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])
  let faces = (req.results ?? []).sorted { $0.boundingBox.width > $1.boundingBox.width }
  guard let f = faces.first, let l = f.landmarks?.leftPupil ?? f.landmarks?.leftEye, let r = f.landmarks?.rightPupil ?? f.landmarks?.rightEye else { print("\(path)\t\(Int(W))\t\(Int(H))\tNOFACE\t\(faces.count)"); continue }
  func pt(_ p: VNFaceLandmarkRegion2D) -> (Double, Double) {
    let a = p.normalizedPoints; let x = a.map{Double($0.x)}.reduce(0,+)/Double(a.count); let y = a.map{Double($0.y)}.reduce(0,+)/Double(a.count)
    let b = f.boundingBox
    return ((Double(b.origin.x)+x*Double(b.width))*W, (1-(Double(b.origin.y)+y*Double(b.height)))*H)
  }
  let (lx,ly)=pt(l); let (rx,ry)=pt(r)
  print("\(path)\t\(Int(W))\t\(Int(H))\t\(lx)\t\(ly)\t\(rx)\t\(ry)\t\(faces.count)\t\(f.confidence)")
}
